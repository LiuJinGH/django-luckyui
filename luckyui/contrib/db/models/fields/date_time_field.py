from django.db.models import fields
from luckyui.contrib import forms as lucky_forms


class DateTimeField(fields.DateTimeField):

    def formfield(self, **kwargs):
        kwargs['form_class'] = lucky_forms.DateTimeField
        kwargs['widget'] = lucky_forms.DateTimeField.widget
        return super().formfield(**kwargs)
