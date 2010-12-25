import re

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.template import Template, Context

from mailer import send_html_mail

from selvbetjening.core.events.models import Event, Option, AttendState, Attend
from selvbetjening.core.models import ListField

import sources

class EmailSpecification(models.Model):
    # source
    event = models.CharField(max_length=64, default='', blank=True,
                             choices=sources.registry.get_choices())

    source_enabled = models.BooleanField(default=False)

    # conditions
    # see condition models below

    # template
    subject = models.CharField(max_length=128)
    body = models.TextField()

    # meta
    date_created = models.DateField(editable=False, auto_now_add=True)
    recipients = models.ManyToManyField(User, editable=False)

    def is_valid(self):
        return False

    @property
    def required_parameters(self):
        parameters = sources.default_parameters

        try:
            source = sources.registry.get(self.event)
            parameters = source['parameters']
        except KeyError:
            pass

        return parameters

    @property
    def conditions(self):
        parameters = self.required_parameters
        conditions = []

        for condition in ALL_CONDITIONS:
            if condition.accepts(parameters):
                try:
                    instance = condition.objects.get(specification=self)
                except condition.DoesNotExist:
                    instance = condition.objects.create(specification_id=1)
                    
                conditions.append(instance)

        return conditions

    def passes_conditions(self, user, **kwargs):
        for condition in self.conditions:
            if not condition.passes(user, **kwargs):
                return False

        return True

    def send_email(self, users, bypass_conditions=False, **kwargs):
        if not hasattr(users, '__iter__'):
            users = [users,]

        email_counter = 0

        for user in users:
            if bypass_conditions or self.passes_conditions(user, **kwargs):
                self._send_email(user, **kwargs)
                email_counter += 1

        return email_counter

    def _send_email(self, user, **kwargs):
        body_plain, body_html = self._compile_body(user=user, **kwargs)

        send_html_mail(self.subject, body_plain, body_html,
                  settings.DEFAULT_FROM_EMAIL, (user.email,))

    def _compile_body(self, user, **kwargs):
        context = Context(kwargs)
        context.update({'user': user})

        body_plain = Template(re.sub(r'<[^>]*?>', '', self.body)).render(context)
        body_html = Template(self.body).render(context)

        return (body_plain, body_html)

    def __unicode__(self):
        return self.subject

class UserConditions(models.Model):
    AGE_COMPARATOR_CHOICES = {'<': ('<', lambda age, argument: age < argument),
                              '=': ('=', lambda age, argument: age == argument),
                              '>': ('>', lambda age, argument: age > argument)}

    specification = models.OneToOneField(EmailSpecification)

    user_age_comparator = models.CharField(max_length='1', default='<',
                                           choices=[(key, AGE_COMPARATOR_CHOICES[key][0])
                                                    for key
                                                    in AGE_COMPARATOR_CHOICES])

    user_age_argument = models.IntegerField(blank=True, default=None, null=True)

    @staticmethod
    def accepts(parameters):
        return User in parameters

    def passes(self, user, **kwargs):
        if self.user_age_argument is None:
            return True

        name, comparator = self.AGE_COMPARATOR_CHOICES[self.user_age_comparator]

        return comparator(user.get_profile().get_age(), self.user_age_argument)

class GenericAttendeeConditions(models.Model):
    class Meta:
        abstract = True

    ATTEND_STATUS_CHOICES = AttendState.get_choices()

    specification = models.OneToOneField(EmailSpecification)

    event = models.ForeignKey(Event, blank=True, null=True, default=None)

    attends_selection_comparator = models.CharField(max_length=12, default='someof',
                                                    choices=(('someof', 'Selected some of'),
                                                             ('allof', 'Selected all of')),)
    attends_selection_argument = models.ManyToManyField(Option, blank=True)

    attends_status = ListField(choices=ATTEND_STATUS_CHOICES, blank=True,
                               default=ATTEND_STATUS_CHOICES[0][0])

    def passes(self, user, attendee=None):
        if self.event is None:
            return True

        try:
            if attendee is None:
                attendee = self.event.attendees.objects.get(user=user)
        except Attend.DoesNotExist:
            return False

        if not attendee.event == self.event:
            return False

        desired_selections = self.attends_selection_argument.objects.all()

        if len(selections) > 0:
            actual_selections = attendee.selections.objects.all()
            hits = 0

            for desired_selection in desired_selections:
                if desired_selection in actual_selections:
                    hits += 1

            if self.attends_selection_comparator == 'someof':
                if hits == 0:
                    return False

            if self.attends_selection_comparator == 'allof':
                if not hits == len(desired_selections):
                    return False

        if len(self.attends_status) > 0:
            if not attendee.status in self.attends_status:
                return False

        return True

class AttendConditions(GenericAttendeeConditions):
    """
    Checks if the user attends a given event.
    """

    @staticmethod
    def accepts(parameters):
        return (Attend not in parameters)

    def passes(self, user, **kwargs):
        return super(AttendConditions, self).passes(user)

class BoundAttendConditions(GenericAttendeeConditions):
    """
    Checks if a user attends a given event and checks the
    event matches with the event passed by the source.
    """

    @staticmethod
    def accepts(parameters):
        return Attend in parameters

    def passes(self, user, **kwargs):
        attendee = kwargs.pop('attendee')
        return super(BoundAttendConditions, self).passes(user, attendee)

ALL_CONDITIONS = [UserConditions, AttendConditions, BoundAttendConditions]

def source_triggered_handler(sender, **kwargs):
    source_key = kwargs.pop('source_key')
    user = kwargs.pop('user')

    specifications = EmailSpecification.objects.filter(event=source_key)

    for specification in specifications:
        specification.send_email(user, **arguments)

sources.source_triggered.connect(source_triggered_handler)