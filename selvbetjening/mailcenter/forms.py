from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from selvbetjening.events.models import Event
from selvbetjening.members.shortcuts import get_or_create_profile

class SendPreviewEmailForm(forms.Form):
    email = forms.EmailField()

class SelectGroupForm(forms.Form):
    group = forms.CharField(max_length=128, label=_('Recipient group'), widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(SelectGroupForm, self).__init__(*args, **kwargs)

        self.fields['group'].widget.choices = [('all', _('All users')),]

        for event in Event.objects.all():
            self.fields['group'].widget.choices.append(('event_' + str(event.id), _('Event: %s') % event.title))

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

        return recipients

class ConfirmGroupForm(SelectGroupForm):
    confirm = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u'Send emails to the selected individuals'))

    class Meta:
        layout = (
            ('', ('confirm', ('group', {'display' : 'hidden'}))),
              )

    def clean_confirm(self):
        """
        Validates that the user accepted the Terms of Service.

        """
        if self.cleaned_data.get('confirm', False):
                return self.cleaned_data['confirm']
        raise forms.ValidationError(_(u'You must confirm the list of recipients before sending to them.'))


