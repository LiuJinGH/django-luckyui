from django.forms import fields
from ..widgets import LuckyImageUpload


class ImageField(fields.ImageField):
    widget = LuckyImageUpload
