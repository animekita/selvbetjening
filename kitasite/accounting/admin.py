from django.contrib import admin

from models import Payment, YearlyRate

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'type')

admin.site.register(Payment, PaymentAdmin)

class YearlyRateAdmin(admin.ModelAdmin):
    list_display = ('year', 'rate')

admin.site.register(YearlyRate, YearlyRateAdmin)