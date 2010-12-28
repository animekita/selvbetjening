# -- encoding: utf-8 --

from django.contrib.admin import StackedInline

from selvbetjening.core.events.models import Invoice, Attend
from selvbetjening.core.invoice.models import InvoiceRevision, Payment

from selvbetjening.sadmin.base.sadmin import SBoundModelAdmin
from selvbetjening.sadmin.events import nav

class InlinePaymentAdmin(StackedInline):  
    model = Payment
    extra = 0
    can_delete = False
    max_num = 0
    readonly_fields = ('created_date', 'amount', 'signee', 'note')

    fieldsets = (
        (None, {
            'fields': (('created_date', 'amount', 'signee', 'note'),),
            }),
    )

class InlineInvoiceRevisionAdmin(StackedInline):
    model = InvoiceRevision
    extra = 0
    can_delete = False
    max_num = 0

def total(invoice):
    return invoice.total_price

def paid(invoice):
    return invoice.paid

class InvoiceAdmin(SBoundModelAdmin):
    class Meta:
        app_name = 'events'
        name = 'invoice'
        model = Invoice
        bound_model = Attend
        bind_key = 'bind_attendee_pk'
        default_views = ()

    readonly_fields = ('name', total, paid)
    exclude = ('user',)
    inlines = [InlinePaymentAdmin, InlineInvoiceRevisionAdmin,]
    
    fieldsets = (
        (None, {
            'fields': ('name', (total, paid)),
            }),
    )

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpattern = patterns('',
            url(r'^$',
                self._wrap_oldadmin_view(self.change_view),
                name='%s_%s_change' % self._url_info)
            )

        return urlpattern

    def change_view(self, request, extra_context=None, **kwargs):
        extra_context = extra_context or {}
        extra_context['menu'] = nav.attendee_menu.render(event_pk=request.bound_object.event.pk,
                                                         attendee_pk=request.bound_object.pk,
                                                         user_pk=request.bound_object.user.pk)

        object_id = str(request.bound_object.invoice.pk)
        return super(InvoiceAdmin, self).change_view(request, object_id, extra_context)