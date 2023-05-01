from django.db import models

from monfaristo.utils.db.models import TimeStampedModel


# Create your models here.
class Transaction(TimeStampedModel):
    symbol = models.CharField(max_length=32)
    symbolyo = models.IntegerField()

    class Meta:
        managed = True
