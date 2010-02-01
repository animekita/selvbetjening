import re

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from tinymce.models import HTMLField

from mailer import send_html_email

# Create your models here.
class Mail(models.Model):
    subject = models.CharField(max_length=128)
    body = HTMLField()
    date_created = models.DateField(editable=False, auto_now_add=True)
    recipients = models.ManyToManyField(User, editable=False)

    def is_draft(self):
        return (len(self.recipients.all()) == 0)
    is_draft.boolean = True

    def send(self, users):
        """
        Sends mails to a list of users, while registering the list of users in the recipients
        relation.

        """
        emails = []
        for user in users:
            emails.append(user.email)
            self.recipients.add(user)
        self._send_mail(emails)

    def send_preview(self, emails):
        self._send_mail(emails)

    def recipient_filter(self, recipients):
        """
        Filter a list of recipient users, dividing them into an "accept" and a "deny" group based
        on previous send e-mail to those users. A touple containing two lists are returned.
        ([accept], [deny])

        """
        accept = []
        deny = []
        current_recipients = self.recipients.all()
        for recipient in recipients:
            if recipient in current_recipients:
                deny.append(recipient)
            else:
                accept.append(recipient)

        return (accept, deny)

    def _send_mail(self, recipients):
        """
        Send e-mails to a list of e-mail adresses.

        """
        body_plain = re.sub(r'<[^>]*?>', '', self.body)
        body_html = render_to_string('mailcenter/email/newsletter_html.txt',
                                     { 'body': self.body })

        send_html_email(self.subject, body_plain, body_html,
                  settings.DEFAULT_FROM_EMAIL, recipients)

    def __unicode__(self):
        return self.subject
