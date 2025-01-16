from django.forms import fields
from ..widgets import LuckySelect


class TypedChoiceField(fields.TypedChoiceField):
    widget = LuckySelect
