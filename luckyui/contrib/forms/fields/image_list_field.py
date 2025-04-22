from django.forms import fields
from ..widgets import LuckyImageListUpload


class ImageListField(fields.JSONField):
    widget = LuckyImageListUpload
