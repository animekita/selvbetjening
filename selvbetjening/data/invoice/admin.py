from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ObjectDoesNotExist

from selvbetjening.core.selvadmin.admin import site

from models import Invoice, InvoiceRevision, Line, Payment
import admin_views

class InvoiceAdmin(ModelAdmin):
    list_display = ('name', 'user', 'total_price', 'paid', 'is_paid')

    fieldsets = (
        (None, {
            'fields' : ('name', 'user',),
        }),)

    raw_id_fields = ('user', )
    search_fields = ('name', 'user__username', 'user__first_name', 'user__last_name')
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
                               url(r'^/report/',
                                   self.admin_site.admin_view(admin_views.invoice_report),
                                   name='%s_%s_report' % info),
                               url(r'^/pay/',
                                   self.admin_site.admin_view(admin_views.invoice_pay),
                                   name='%s_%s_pay' % info),
                               )

        urlpatterns += super(InvoiceAdmin, self).get_urls()

        return urlpatterns

site.register(Invoice, InvoiceAdmin)

class LineInlines(TabularInline):
    model = Line

    def get_formset(self, request, obj=None, **kwargs):
        class ExtendedBaseInlineFormSet(BaseInlineFormSet):
            def __init__(self, **kwargs):
                if request.GET.has_key('invoice') and kwargs.has_key('data'):
                    kwargs['data']['line_set-INITIAL_FORMS'] = 0

                super(ExtendedBaseInlineFormSet, self).__init__(**kwargs)

            def get_queryset(self):
                if request.method=='GET' and request.GET.has_key('invoice'):
                    try:
                        invoice = Invoice.objects.get(pk=request.GET.get('invoice'))
                        lines = []
                        for line in invoice.latest_revision.line_set.all():
                            lines.append(Line(description=line.description, price=line.price))
                        return lines
                    except ObjectDoesNotExist:
                        pass

                return super(ExtendedBaseInlineFormSet, self).get_queryset()

        self.formset = ExtendedBaseInlineFormSet
        return super(LineInlines, self).get_formset(request, obj, **kwargs)

class InvoiceRevisionAdmin(ModelAdmin):
    list_display = ('id', 'invoice', 'user', 'created_date')
    inlines = [LineInlines,]
    date_hierarchy = 'created_date'

    def user(self, revision):
        return revision.invoice.user
    user.admin_order_field = 'invoice__user'

site.register(InvoiceRevision, InvoiceRevisionAdmin)

class PaymentAdmin(ModelAdmin):
    list_display = ('user', 'invoice', 'revision', 'amount', 'signee', 'note')
    search_fields = ('revision__invoice__name', 'signee__username', 'note',)
    date_hierarchy = 'created_date'

    def user(self, payment):
        return payment.revision.invoice.user
    user.admin_order_field = 'revision__invoice__user'

    def invoice(self, payment):
        return payment.revision.invoice
    invoice.admin_order_field = 'revision_invoice'

site.register(Payment, PaymentAdmin)