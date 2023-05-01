from django.db import models
from monfaristo.utils.db.enum import ChoiceEnum

from monfaristo.utils.db.models import TimeStampedModel


class Ticker(models.Model):
    class MarketChoice(ChoiceEnum):
        BIST = "BIST"
        NASDAQ = "NASDAQ"
        NYSE = "NYSE"
        CRYPTO = "CRYPTO"
        OTHER = "OTHER"

    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    market = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        choices=MarketChoice.choices(),
        default=MarketChoice.BIST.value,
    )

    def __str__(self):
        return f'{self.code.upper()} ({self.market})'

    class Meta:
        db_table = "ticker"


class Broker(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(null=True)
    description = models.TextField(null=True, default=None, blank=True)

    def __str__(self):
        return f'{self.title.title()}'

    class Meta:
        db_table = "broker"


class Currency(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.code.upper()} ({self.title.title()})'

    class Meta:
        db_table = "currency"


class Transaction(TimeStampedModel):
    class TypeChoice(ChoiceEnum):
        DEPOSIT = "DEPOSIT"
        WITHDRAW = "WITHDRAW"
        BUY = "BUY"
        SELL = "SELL"

    ticker = models.ForeignKey(
        "journal.Ticker", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    type = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=TypeChoice.choices(),
        default=TypeChoice.BUY.value,
    )
    lot = models.FloatField(max_length=24)
    price = models.FloatField(max_length=24)
    fee = models.FloatField(max_length=24)
    currency = models.ForeignKey(
        "journal.Currency",
        on_delete=models.DO_NOTHING,
        related_name="+",
    )
    broker = models.ForeignKey(
        "journal.Broker",
        on_delete=models.DO_NOTHING,
        related_name="+",
    )
    description = models.TextField()

    class Meta:
        managed = False
        verbose_name = "transaction"
        verbose_name_plural = "transactions"
        db_table = "journal_transaction"
        indexes = [
            models.Index(fields=["ticker"], name="ix_ticker"),
            models.Index(fields=["broker"], name="ix_broker"),
            models.Index(fields=["type"], name="ix_type"),
        ]
