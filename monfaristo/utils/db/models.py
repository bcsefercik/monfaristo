from django.db import models

from monfaristo.utils.db.fields import AutoCreatedTimestampField, AutoLastModifiedTimestampField


class TimeStampedModel(models.Model):
    created = AutoCreatedTimestampField("created")
    modified = AutoLastModifiedTimestampField("modified")

    class Meta:
        abstract = True
        managed = False
