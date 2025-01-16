from django.db.models import fields
from luckyui.contrib import forms as lucky_forms


class BooleanField(fields.BooleanField):
    def formfield(self, **kwargs):
        kwargs['form_class'] = lucky_forms.BooleanField
        kwargs['required'] = False
        return super().formfield(**kwargs)
