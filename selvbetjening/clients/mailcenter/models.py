import re

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from mailer import send_html_mail

import sources
import conditions

class EmailSpecification(models.Model):
    # source
    event = models.CharField(max_length=64, default='', blank=True,
                             choices=[(key, sources.sources[key][0]) for key in sources.sources])

    source_enabled = models.BooleanField(default=False)

    # conditions
    # see foreign key on Condition model

    # template
    subject = models.CharField(max_length=128)
    body = models.TextField()

    # meta
    date_created = models.DateField(editable=False, auto_now_add=True)
    recipients = models.ManyToManyField(User, editable=False)

    def is_valid(self):
        return False

    def passes_conditions(self, user, **kwargs):
        return True

    def send_email(self, users, bypass_conditions=False, **kwargs):
        if not hasattr(users, '__iter__'):
            users = [users,]

        if not bypass_conditions:
            users = [user for user in users if self.passes_conditions(user, **kwargs)]

        self._send_email(users)

        return len(users)

    def _send_email(self, recipients):
        body_plain = re.sub(r'<[^>]*?>', '', self.body)
        body_html = render_to_string('mailcenter/email/newsletter_html.txt',
                                     { 'body': self.body })

        send_html_mail(self.subject, body_plain, body_html,
                  settings.DEFAULT_FROM_EMAIL, recipients)

    def __unicode__(self):
        return self.subject

class Condition(models.Model):
    specification = models.ForeignKey(EmailSpecification, related_name='conditions')

    negate_condition = models.BooleanField(default=False)

    field = models.CharField(max_length=256)
    comparator = models.CharField(max_length=256)
    argument = models.CharField(max_length=256)

    @property
    def field_choices(self):
        choices = []
        parameters = ['user',]
        import wingdbstub
        for parameter in parameters:
            name, param_type, fields = conditions.parameters[parameter]
            choices.append((name, [(field[0], field[1]) for field in fields]))

        return choices

