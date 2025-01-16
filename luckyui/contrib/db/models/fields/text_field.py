from django.db.models import fields
from luckyui.contrib import forms as lucky_forms


class TextField(fields.TextField):

    def formfield(self, **kwargs):
        kwargs['form_class'] = lucky_forms.TextField
        kwargs['widget'] = lucky_forms.TextField.widget
        kwargs['max_length'] = self.max_length
        return super().formfield(**kwargs)
