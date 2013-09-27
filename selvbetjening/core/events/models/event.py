
from datetime import date

from django.db import models
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext as _


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

    title = models.CharField(_(u'title'), max_length=255)
    description = models.TextField(_(u'description'), blank=True)

    startdate = models.DateField(_(u'start date'), blank=True, null=True)
    enddate = models.DateField(_(u'end date'), blank=True, null=True)

    # constraints and effects
    move_to_accepted_policy = \
        models.CharField(max_length=32,
                         default=AttendeeAcceptPolicy.always,
                         choices=AttendeeAcceptPolicy.get_choices())

    maximum_attendees = models.IntegerField(_('Maximum attendees'), default=0)
    registration_open = models.BooleanField(_(u'registration open'))

    # display
    show_custom_signup_message = models.BooleanField(default=False)
    custom_signup_message = models.TextField(
        blank=True,
        help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev, attendee'
    )

    show_custom_change_message = models.BooleanField(default=False)
    custom_change_message = models.TextField(
        blank=True,
        help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev, attendee'
    )

    show_custom_status_page = models.BooleanField(default=False)
    custom_status_page = models.TextField(
        blank=True,
        help_text=_('The following variables are available: %s.') % u'event, user, invoice_rev, attendee'
    )

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

    def __unicode__(self):
        return _(u'%s') % self.title

