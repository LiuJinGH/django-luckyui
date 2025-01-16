from django.forms import fields
from ..widgets import LuckyNumberInput


class IntegerField(fields.IntegerField):
    widget = LuckyNumberInput
