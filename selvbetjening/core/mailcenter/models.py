import logging
import re
import markdown

from django.conf import settings
from django.db import models
from django.template import Template, Context, loader
import sys

from selvbetjening.core.mail import send_mail

logger = logging.getLogger('selvbetjening.email')


class EmailSpecification(models.Model):
    BODY_FORMAT_CHOICES = (
        ('html', 'HTML'),
        ('markdown', 'Markdown')
    )

    CONTEXT_CHOICES = (
        ('user', 'User'),
        ('attendee', 'Attendee')
    )

    # template
    subject = models.CharField(max_length=128)
    body = models.TextField()

    body_format = models.CharField(max_length=32, choices=BODY_FORMAT_CHOICES, default='markdown')

    # context
    template_context = models.CharField(max_length=32, choices=CONTEXT_CHOICES, default='user')

    # meta
    date_created = models.DateField(editable=False, auto_now_add=True)

    def send_email_user(self, user, internal_sender_id):
        if self.template_context == 'attendee':
            raise ValueError

        ok, email, err = self.render_user(user)

        if not ok:
            # Warn an admin and log the error silently

            logger.exception('Failure rendering e-mail (template pk: %s) -- Addressed to %s', self.pk, user.email, exc_info=err, extra={
                'related_user': user})

            return

        instance = self._send_mail(user.email, email, internal_sender_id)

        logger.info('E-mail queued (%s) -- Addressed to %s', email['subject'], user.email,
                    extra={
                        'related_user': user,
                        'related_email': instance
                    })

    def send_email_attendee(self, attendee, internal_sender_id):

        ok, email, err = self.render_attendee(attendee)

        if not ok:
            # Warn an admin and log the error silently

            logger.exception('Failure rendering e-mail (template pk: %s) -- Addressed to %s', self.pk, attendee.user.email, exc_info=err, extra={
                'related_user': attendee.user,
                'related_attendee': attendee})

            return

        instance = self._send_mail(attendee.user.email, email, internal_sender_id)

        logger.info('E-mail queued (%s) -- Addressed to %s', email['subject'], attendee.user.email,
                    extra={
                        'related_user': attendee.user,
                        'related_attendee': attendee,
                        'related_email': instance
                    })

    def _send_mail(self, to_address, email, internal_sender_id):

        mails = send_mail(email['subject'],
                          email['body_plain'],
                          settings.DEFAULT_FROM_EMAIL,
                          [to_address],
                          body_html=email['body_html'],
                          internal_sender_id=internal_sender_id)

        return mails[0]

    def render_user(self, user):
        """
        Renders the e-mail template using a user object as source.

        An error is thrown if the template context is Attendee.
        """

        if self.template_context == 'attendee':
            raise ValueError

        return self._render(self._get_context(user))

    def render_attendee(self, attendee):
        """
        Renders the e-mail template using a user object as source.
        """

        return self._render(self._get_context(attendee.user, attendee=attendee))

    def render_dummy(self):

        context = {
            # user context
            'username': 'johndoe',
            'full_name': 'John Doe',
            'email': 'johndoe@example.org',

            # attendee.event context
            'event_title': 'Dummy Event',
            'invoice_plain': 'INVOICE',
            'invoice_html': 'INVOICE_HTML'
        }

        return self._render(context)

    def _get_context(self, user, attendee=None):
        # lazy import, prevent circular import in core.events
        from selvbetjening.core.events.options.dynamic_selections import SCOPE, dynamic_selections

        context = {
            # user context
            'username': user.username,
            'full_name': ('%s %s' % (user.first_name, user.last_name)).strip(),
            'email': user.email
        }

        if attendee is not None:

            invoice = dynamic_selections(SCOPE.VIEW_USER_INVOICE, attendee)

            invoice_html = loader.render_to_string('events/parts/invoice.html', {
                'attendee': attendee,
                'invoice': invoice
            })

            invoice_text = loader.render_to_string('events/parts/invoice_text.html', {
                'attendee': attendee,
                'invoice': invoice
            })

            context.update({
                # attendee.event context
                'event_title': attendee.event.title,
                'attendee': attendee,
                'invoice_plain': invoice_text,
                'invoice_html': invoice_html,
            })

            for option, selection in invoice:
                context['selected_%s' % option.pk] = selection is not None

        return context

    def _render(self, context):

        context = Context(context)

        try:
            email = {
                'subject': self.subject,
                'body_plain': self._get_rendered_body_plain(context),
                'body_html': self._get_rendered_body_html(context)
            }

            return True, email, None

        except Exception:
            return False, None, sys.exc_info()

    def _get_rendered_body_plain(self, context):

        if self.body_format == 'markdown':
            body = self.body
        else:
            body = re.sub(r'<[^>]*?>', '', self.body)

        context['invoice'] = context.get('invoice_plain', None)

        return Template(body).render(context)

    def _get_rendered_body_html(self, context):

        if self.body_format == 'markdown':
            body = markdown.markdown(self.body)
        else:
            body = self.body

        context['invoice'] = context.get('invoice_html', None)

        return Template(body).render(context)

    def __unicode__(self):
        return self.subject
