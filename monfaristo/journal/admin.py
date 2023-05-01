from django.contrib import admin

from monfaristo.journal.models import Transaction


class TransactionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Transaction, TransactionAdmin)
