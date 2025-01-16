from django.forms import fields
from ..widgets import LuckyInput


class CharField(fields.CharField):
    widget = LuckyInput
