from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from selvbetjening.data.events.models import Event, OptionGroup
from selvbetjening.data.members.shortcuts import get_or_create_profile

class SelectGroupForm(forms.Form):
    group = forms.CharField(max_length=128, label=_('Recipient group'), widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(SelectGroupForm, self).__init__(*args, **kwargs)

        self.fields['group'].widget.choices = [('all', _('All users')),]

        for event in Event.objects.all():
            self.fields['group'].widget.choices.append(('event_' + str(event.id), _(u'Event: %s') % event.title))

            for optiongroup in event.optiongroup_set.all():
                og_choice = ('optiongroup_%s' % str(optiongroup.pk), _(u'Event: %s - Optiongroup: %s') % (event.title, optiongroup.name))
                self.fields['group'].widget.choices.append(og_choice)

    def get_selected_recipients(self):
        recipients = []
        group = self.cleaned_data.get('group', '')

        def append_user(user):
            profile = get_or_create_profile(user)
            if profile.send_me_email == True:
                recipients.append(user)

        if group == 'all':
            users = User.objects.all().exclude(is_active=0)
            for user in users:
                if user.email != '':
                    append_user(user)

        elif group.startswith('event_') and len(group) > 6:
            try:
                event = Event.objects.get(pk=group[6:])
                for attendee in event.attend_set.all():
                    if attendee.user.email != '':
                        append_user(attendee.user)
            except Event.DoesNotExist:
                pass

        elif group.startswith('optiongroup_') and len(group) > 12:
            try:
                optiongroup = OptionGroup.objects.get(pk=group[12:])
                for attendee in optiongroup.attendees:
                    if attendee.user.email != '':
                        append_user(attendee.user)
            except OptionGroup.DoesNotExist:
                pass

        return recipients




