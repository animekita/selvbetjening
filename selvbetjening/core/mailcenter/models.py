import re

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

    def _send_email(self, user, internal_sender_id=None, **kwargs):
        subject, body_plain, body_html = self._compile_content(user=user, **kwargs)

        send_mail(subject,
                  body_plain,
                  settings.DEFAULT_FROM_EMAIL,
                  [user.email],
                  body_html=body_html,
                  internal_sender_id=internal_sender_id)

    def _compile_content(self, user, **kwargs):
        # TODO add support for markdown
        
        context = Context(kwargs)
        context.update({'user': user})

        body_plain = Template(re.sub(r'<[^>]*?>', '', self.body)).render(context)
        body_html = Template(self.body).render(context)

        subject = Template(self.subject).render(context)

        return subject, body_plain, body_html

    def __unicode__(self):
        return self.subject
