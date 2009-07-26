from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ObjectDoesNotExist

from models import Invoice, InvoiceRevision, Line

class InvoiceAdmin(ModelAdmin):
    list_display = ('name', 'user', 'total_price', 'paid', 'is_paid')

    fieldsets = (
        (None, {
            'fields' : ('name', 'user',),
        }),)

    raw_id_fields = ('user', )

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
    inlines = [LineInlines,]

class PaymentAdmin(ModelAdmin):
    pass

