from django.forms import fields
from ..widgets import LuckyDateTimePicker


class DateTimeField(fields.SplitDateTimeField):
    widget = LuckyDateTimePicker
