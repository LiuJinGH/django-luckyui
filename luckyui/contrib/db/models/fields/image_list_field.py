import uuid

from django.db import models
from luckyui.contrib import forms as lucky_forms


class ImageListField(models.JSONField):

    def __init__(
        self,
        verbose_name=None,
        name=None,
        encoder=None,
        decoder=None,
        upload_to=None,
        **kwargs,
    ):
        self.upload_to = upload_to
        super().__init__(verbose_name, name, encoder, decoder, **kwargs)

    def formfield(self, **kwargs):
        kwargs['form_class'] = lucky_forms.ImageListField
        kwargs['widget'] = lucky_forms.ImageListField.widget
        return super().formfield(**kwargs)
