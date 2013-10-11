import re

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.template import Template, Context
from django.utils.translation import ugettext as _

from mailer import send_html_mail

from selvbetjening.core.events.models import Event, Option, AttendState, Attend
from selvbetjening.core.models import ListField

import sources


class EmailSpecification(models.Model):

    # source
    event = models.CharField(max_length=64, default='', blank=True,
                             choices=sources.registry)

    source_enabled = models.BooleanField(default=False)

    # conditions
    # see condition models below

    # template
    subject = models.CharField(max_length=128)
    body = models.TextField()

    # meta
    date_created = models.DateField(editable=False, auto_now_add=True)
    recipients = models.ManyToManyField(User, editable=False)

    # recipients
    send_to_user = models.BooleanField(default=True)
    other_recipients = models.CharField(blank=True, max_length=255,
                                        help_text=_('Comma separated list of recipient e-mails'))

    @property
    def required_parameters(self):
        parameters = sources.default_parameters

        try:
            source = sources.registry.get(self.event)
            parameters = source.parameters
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
                    instance = condition.objects.create(specification_id=self.pk)

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
        subject, body_plain, body_html = self._compile_content(user=user, **kwargs)

        recipients = []

        if self.other_recipients.strip() != '':
            recipients = self.other_recipients.split(',')

        if self.send_to_user:
            recipients.append(user.email)

        send_html_mail(subject, body_plain, body_html,
                  settings.DEFAULT_FROM_EMAIL, recipients)

    def _compile_content(self, user, **kwargs):
        context = Context(kwargs)
        context.update({'user': user})

        body_plain = Template(re.sub(r'<[^>]*?>', '', self.body)).render(context)
        body_html = Template(self.body).render(context)

        subject = Template(self.subject).render(context)

        return (subject, body_plain, body_html)

    def __unicode__(self):
        return self.subject

class UserConditions(models.Model):
    AGE_COMPARATOR_CHOICES = {'<': ('<', lambda age, argument: age < argument),
                              '=': ('=', lambda age, argument: age == argument),
                              '>': ('>', lambda age, argument: age > argument)}

    specification = models.OneToOneField(EmailSpecification)

    user_age_comparator = models.CharField(max_length='1', blank=True,
                                           choices=[(key, AGE_COMPARATOR_CHOICES[key][0])
                                                    for key
                                                    in AGE_COMPARATOR_CHOICES])

    user_age_argument = models.IntegerField(blank=True, default=None, null=True)

    @staticmethod
    def accepts(parameters):
        return User in parameters

    def passes(self, user, **kwargs):
        if self.user_age_argument is None or self.user_age_comparator == '':
            return True

        name, comparator = self.AGE_COMPARATOR_CHOICES[self.user_age_comparator]

        return comparator(user.get_profile().get_age(), self.user_age_argument)


class GenericAttendeeConditions(models.Model):
    class Meta:
        abstract = True

    ATTEND_STATE_CHOICES = AttendState.get_choices()

    specification = models.OneToOneField(EmailSpecification)

    event = models.ForeignKey(Event, blank=True, null=True, default=None)

    attends_selection_comparator = models.CharField(max_length=12, blank=True,
                                                    choices=(('someof', 'Selected some of'),
                                                             ('allof', 'Selected all of')),)
    attends_selection_argument = models.ManyToManyField(Option, blank=True)

    attends_state = ListField(choices=ATTEND_STATE_CHOICES, blank=True,
                              default=ATTEND_STATE_CHOICES[0][0], null=True)

    def passes(self, user, attendee=None, **kwargs):
        if self.event is None:
            return True

        try:
            if attendee is None:

                attend_cache = kwargs.pop('attend_cache', None)

                if attend_cache is None:
                    attendee = self.event.attendees.get(user=user)
                else:
                    if self.event.pk not in attend_cache:
                        attend_cache[self.event.pk] = dict()
                        for attendee in Attend.objects.filter(event=self.event.pk).select_related():
                            attend_cache[self.event.pk][attendee.user.pk] = attendee

                    if user.pk in attend_cache[self.event.pk]:
                        attendee = attend_cache[self.event.pk][user.pk]
                    else:
                        return False

        except Attend.DoesNotExist:
            return False

        # event check
        if attendee.event != self.event:
            return False

        # selections check
        if not hasattr(self, '_attends_selection_argument_cache'):
            self._attends_selection_argument_cache = [option.pk for option in self.attends_selection_argument.all()]

        desired_options = self._attends_selection_argument_cache

        if len(desired_options) > 0:
            actual_selections = attendee.selections.all()
            hits = 0

            for actual_selection in actual_selections:
                if actual_selection.option.pk in desired_options:
                    hits += 1

            if self.attends_selection_comparator == 'someof':
                if hits == 0:
                    return False

            if self.attends_selection_comparator == 'allof':
                if hits != len(desired_options):
                    return False

        if self.attends_state is not None and len(self.attends_state) > 0:
            if not attendee.state in self.attends_state:
                return False

        return True


class AttendConditions(GenericAttendeeConditions):
    """
    Checks if the user attends a given event.
    """

    @staticmethod
    def accepts(parameters):
        return Attend not in parameters

    def passes(self, user, **kwargs):
        return super(AttendConditions, self).passes(user, **kwargs)


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
    kwargs = kwargs.pop('kwargs')

    specifications = EmailSpecification.objects.filter(event=source_key,
                                                       source_enabled=True)

    for specification in specifications:
        specification.send_email(user, **kwargs)

sources.source_triggered.connect(source_triggered_handler)