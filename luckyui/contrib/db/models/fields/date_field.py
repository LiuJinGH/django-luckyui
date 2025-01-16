from django.db.models import fields
from luckyui.contrib import forms as lucky_forms


class DateField(fields.DateField):

    def formfield(self, **kwargs):
        kwargs['form_class'] = lucky_forms.DateField
        kwargs['widget'] = lucky_forms.DateField.widget
        return super().formfield(**kwargs)
