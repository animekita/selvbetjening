
from datetime import date

from django.db import models
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext as _

from selvbetjening.core.mailcenter.models import EmailSpecification


class Group(models.Model):

    class Meta:
        app_label = 'events'

    name = models.CharField(_(u'name'), max_length=255)

    def __unicode__(self):
        return self.name


class AttendeeAcceptPolicy(object):
    manual = 'manual'
    always = 'always'
    on_payment = 'on_payment'

    @staticmethod
    def get_choices():
        return (
            ('manual', _(u'Move attendees to accepted list manually')),
            ('on_payment', _(u'Move attendees when a payment have been made')),
            ('always', _(u'Always move to accepted list'))
        )


class Event(models.Model):

    class Meta:
        app_label = 'events'

    group = models.ForeignKey(Group, blank=True, null=True)

    # presentation

    title = models.CharField(_(u'title'), max_length=255)
    tagline = models.TextField(_(u'tagline'), blank=True)
    description = models.TextField(_(u'description'), blank=True)

    location = models.CharField(_('location'), max_length=255, blank=True)
    location_link = models.URLField(_('location map url'), blank=True)

    startdate = models.DateField(_(u'start date'))
    enddate = models.DateField(_(u'end date'))

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)

    # constraints and effects
    move_to_accepted_policy = \
        models.CharField(max_length=32,
                         default=AttendeeAcceptPolicy.always,
                         choices=AttendeeAcceptPolicy.get_choices())

    registration_open = models.BooleanField(_(u'registration open'), default=False)
    is_visible = models.BooleanField(default=False)

    # display
    show_custom_signup_message = models.BooleanField(default=False)
    custom_signup_message = models.TextField(
        blank=True,
        help_text=_('The following variables are available: %s.') % u'event, user, attendee'
    )

    show_custom_change_message = models.BooleanField(default=False)
    custom_change_message = models.TextField(
        blank=True,
        help_text=_('The following variables are available: %s.') % u'event, user, attendee'
    )

    show_custom_status_page = models.BooleanField(default=False)
    custom_status_page = models.TextField(
        blank=True,
        help_text=_('The following variables are available: %s.') % u'event, user, attendee'
    )

    # E-mail notifications

    notify_on_registration = \
        models.ForeignKey(EmailSpecification, blank=True, null=True, related_name='notify_event_on_registration')
    notify_on_registration_update = \
        models.ForeignKey(EmailSpecification, blank=True, null=True, related_name='notify_event_on_registration_update')
    notify_on_payment = \
        models.ForeignKey(EmailSpecification, blank=True, null=True, related_name='notify_event_on_payment_registration')

    def send_notification_on_registration(self, attendee):
        if self.notify_on_registration is not None:
            self.notify_on_registration.send_email_attendee(attendee, 'event.notify.on_registration')

    def send_notification_on_registration_update(self, attendee):
        if self.notify_on_registration_update is not None:
            self.notify_on_registration_update.send_email_attendee(attendee, 'event.notify.on_registration_update')

    def send_notification_on_payment(self, attendee):
        if self.notify_on_payment is not None:
            self.notify_on_payment.send_email_attendee(attendee, 'event.notify.on_payment')

    # Special

    @property
    def has_special(self):
        return self.optiongroups.filter(is_special=True).exists()

    @property
    def attendees(self):
        return self.attend_set.all().order_by('id')

    @property
    def optiongroups(self):
        return self.optiongroup_set.all()

    # event state
    def has_been_held(self):
        if self.enddate is None:
            return False

        return self.enddate < date.today()

    def is_registration_open(self):
        return self.registration_open and not self.has_been_held()

    def has_options(self):
        return self.optiongroups.count() > 0

    # attendee management

    def is_attendee(self, user):
        if isinstance(user, AnonymousUser):
            return False
        else:
            return self.attend_set.filter(user=user).count() == 1

    # event management

    def copy_and_mutate_self(self):

        optiongroups = list(self.optiongroup_set.all())

        self.pk = None
        self.title = '%s (copy)' % self.title
        self.is_visible = False
        self.save()

        for group in optiongroups:

            options = list(group.options)

            group.pk = None
            group.save()

            self.optiongroup_set.add(group)

            for option in options:

                suboptions = list(option.suboptions)

                option.pk = None
                option.save()

                group.option_set.add(option)

                for suboption in suboptions:

                    suboption.pk = None
                    suboption.save()

                    option.suboption_set.add(suboption)

    def __unicode__(self):
        return _(u'%s') % self.title


