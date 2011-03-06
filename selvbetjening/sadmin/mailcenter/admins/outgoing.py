from django.utils.translation import ugettext as _

from selvbetjening.sadmin.base.sadmin import SModelAdmin

from mailer.models import Message

class OutgoingAdmin(SModelAdmin):
    class Meta:
        app_name = 'mailcenter'
        name = 'outgoing'
        model = Message
        default_views = ('list', 'change',)
        
        display_name = _(u'Outgoing E-mail')
        display_name_plural = _(u'Outgoing E-mails')

    list_display = ('to_address', 'subject',)
    search_fields = ('subject', 'to_address')
    readonly_fields = ('subject', 'to_address', 'from_address', 'message_body', 'message_body_html', 'priority', 'when_added')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _(u'Outgoing E-mails')
        return super(OutgoingAdmin, self).changelist_view(request, extra_context)