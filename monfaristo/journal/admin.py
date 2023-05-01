from django.contrib import admin

from monfaristo.journal.models import Transaction, Ticker, Broker, Currency


class TransactionAdmin(admin.ModelAdmin):
    pass


class TickerAdmin(admin.ModelAdmin):
    pass


class BrokerAdmin(admin.ModelAdmin):
    pass


class CurrencyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Ticker, TickerAdmin)
admin.site.register(Broker, BrokerAdmin)
admin.site.register(Currency, CurrencyAdmin)
