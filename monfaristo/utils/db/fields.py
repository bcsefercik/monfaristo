import django.utils.timezone
from django.db import models


class UnixDateTimeField(models.DateTimeField):
    description = "Unix timestamp integer to datetime object"

    def db_type(self, connection):
        return "timestamp"

    def get_internal_type(self):
        return "DateTimeField"


class AutoCreatedTimestampField(UnixDateTimeField):
    """
    A DateTimeField that automatically populates itself at
    object creation.

    By default, sets editable=False, default=datetime.now.

    """

    def db_type(self, connection):
        return "TIMESTAMP default CURRENT_TIMESTAMP"

    def __init__(
        self, *args, editable=False, default=django.utils.timezone.now, **kwargs
    ):
        super().__init__(*args, editable=editable, default=default, **kwargs)


class AutoLastModifiedTimestampField(AutoCreatedTimestampField):
    """
    A DateTimeField that updates itself on each save() of the model.

    By default, sets editable=False and default=datetime.now.

    """

    def db_type(self, connection):
        return "TIMESTAMP default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP"

    def pre_save(self, model_instance, add):
        value = django.utils.timezone.now()
        setattr(model_instance, self.attname, value)
        return value


class AutoCreatedTimestampFieldWithoutDefault(UnixDateTimeField):
    """
    A DateTimeField that automatically populates itself at
    object creation.

    By default, sets editable=False, default=None

    """

    def db_type(self, connection):
        return "TIMESTAMP"

    def __init__(self, *args, editable=False, default=None, **kwargs):
        super().__init__(*args, editable=editable, default=default, **kwargs)
