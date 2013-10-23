import re
import markdown

from django.conf import settings
from django.db import models
from django.template import Template, Context

from selvbetjening.core.mail import send_mail


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

        email = self.render_user(user)
        self._send_mail(user.email, email, internal_sender_id)

    def send_email_attendee(self, attendee, internal_sender_id):

        email = self.render_attendee(attendee)
        self._send_mail(attendee.user.email, email, internal_sender_id)

    def _send_mail(self, to_address, email, internal_sender_id):

        send_mail(email['subject'],
                  email['body_plain'],
                  settings.DEFAULT_FROM_EMAIL,
                  [to_address],
                  body_html=email['body_html'],
                  internal_sender_id=internal_sender_id)

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
            'invoice': []
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
            context.update({
                # attendee.event context
                'event_title': attendee.event.title,
                'invoice': dynamic_selections(SCOPE.VIEW_USER_INVOICE, attendee)
            })

        return context

    def _render(self, context):

        context = Context(context)

        email = {
            'subject': self.subject,
            'body_plain': self._get_rendered_body_plain(context),
            'body_html': self._get_rendered_body_html(context)
        }

        return email

    def _get_rendered_body_plain(self, context):

        if self.body_format == 'markdown':
            body = self.body
        else:
            body = re.sub(r'<[^>]*?>', '', self.body)

        return Template(body).render(context)

    def _get_rendered_body_html(self, context):

        if self.body_format == 'markdown':
            body = markdown.markdown(self.body)
        else:
            body = self.body

        return Template(body).render(context)

    def __str__(self):
        return self.subject
