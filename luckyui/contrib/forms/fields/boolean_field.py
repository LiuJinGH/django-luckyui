from django.forms import fields
from ..widgets import LuckySwitch


class BooleanField(fields.BooleanField):
    widget = LuckySwitch
