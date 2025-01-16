from django.forms import fields
from ..widgets import LuckyTextarea


class TextField(fields.CharField):
    widget = LuckyTextarea
