from django.contrib import admin

from models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'type')

class YearlyRateAdmin(admin.ModelAdmin):
    list_display = ('year', 'rate')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    template = 'admin/accounting/payment/edit_inline.html'