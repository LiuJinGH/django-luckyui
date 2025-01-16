from django.forms import fields
from ..widgets import LuckyDatePicker


class DateField(fields.DateField):
    widget = LuckyDatePicker
