from django.contrib import admin

from models import Currency, CurrencyRate


class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ('original_currency', 'target_currency', 'rate')
    list_filter = ('original_currency', 'target_currency')


admin.site.register(Currency)
admin.site.register(CurrencyRate, CurrencyRateAdmin)
