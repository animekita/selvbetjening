from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from selvbetjening.sadmin.mailcenter import nav
from selvbetjening.sadmin.base.sadmin import SAdminContext, SModelAdmin

from mailer.models import Message

class MailerAdmin(SModelAdmin):
    class Meta:
        app_name = 'mailcenter'
        name = 'message'
        model = Message
        default_views = ('list', 'change')

    list_display = ('subject',)
    search_fields = ('subject', 'to_address')
    readonly_fields = ('subject', 'to_address', 'from_address', 'message_body', 'message_body_html', 'priority', 'when_added')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.emails_menu.render()
        return super(MailerAdmin, self).changelist_view(request, extra_context)