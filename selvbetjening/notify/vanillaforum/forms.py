from django import forms
from django.utils.translation import ugettext as _

from uni_form.helpers import FormHelper, Submit, Fieldset, Layout, Row

from selvbetjening.viewbase.forms.helpers import InlineFieldset

from models import Settings

class SettingsForm(forms.ModelForm):

    class Meta:
        model = Settings
        exclude = ('user', 'picture')


    notify_comment_discussions_popup = forms.BooleanField(required=False, label='Popup')
    notify_comment_discussions_email = forms.BooleanField(required=False, label='E-mail')

    notify_mentioned_in_titles_popup = forms.BooleanField(required=False, label='Popup')
    notify_mentioned_in_titles_email = forms.BooleanField(required=False, label='E-mail')

    notify_mentioned_in_comments_popup = forms.BooleanField(required=False, label='Popup')
    notify_mentioned_in_comments_email = forms.BooleanField(required=False, label='E-mail')

    notify_comment_bookmarked_popup = forms.BooleanField(required=False, label='Popup')
    notify_comment_bookmarked_email = forms.BooleanField(required=False, label='E-mail')

    notify_new_discussion_email = forms.BooleanField(required=False, label='E-mail')

    notify_private_message_popup = forms.BooleanField(required=False, label='Popup')
    notify_private_message_email = forms.BooleanField(required=False, label='E-mail')

    notify_private_message_added_popup = forms.BooleanField(required=False, label='Popup')
    notify_private_message_added_email = forms.BooleanField(required=False, label='E-mail')

    layout = Layout(
        InlineFieldset(_(u'Notify me when people comment on my discussions'),
                       Row('notify_comment_discussions_popup',
                           'notify_comment_discussions_email')),

        InlineFieldset(_(u'Notify me when people mention me in discussion titles'),
                       Row('notify_mentioned_in_titles_popup',
                           'notify_mentioned_in_titles_email')),

        InlineFieldset(_(u'Notify me when people mention me in comments'),
                       Row('notify_mentioned_in_comments_popup',
                           'notify_mentioned_in_comments_email')),

        InlineFieldset(_(u'Notify me when people comment on my bookmarked discussions'),
                       Row('notify_comment_bookmarked_popup',
                           'notify_comment_bookmarked_email')),

        InlineFieldset(_(u'Notify me when people start new discussions'),
                       'notify_new_discussion_email'),

        InlineFieldset(_(u'Notify me of private messages'),
                       Row('notify_private_message_popup',
                           'notify_private_message_email')),

        InlineFieldset(_(u'Notify me when I am added to private conversations'),
                       Row('notify_private_message_added_popup',
                           'notify_private_message_added_email')),
    )

    submit = Submit('submit_change', _('Opdater'))

    helper = FormHelper()
    helper.add_layout(layout)
    helper.add_input(submit)
    helper.use_csrf_protection = True