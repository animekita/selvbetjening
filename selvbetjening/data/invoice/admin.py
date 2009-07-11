from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.auth.models import User

from models import Invoice, InvoiceRevision, Line

class InvoiceAdmin(ModelAdmin):
    list_display = ('name', 'user', 'total_price', 'is_paid', 'dropped', 'managed')
    list_filter = ('dropped', 'managed')

class LineInlines(TabularInline):
    model = Line
    
class InvoiceRevisionAdmin(ModelAdmin):
    inlines = [LineInlines,]
