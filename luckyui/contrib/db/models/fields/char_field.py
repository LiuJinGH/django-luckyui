from django.db.models import fields
from luckyui.contrib import forms as lucky_forms


class CharField(fields.CharField):

    def formfield(self, **kwargs):
        kwargs['form_class'] = lucky_forms.CharField
        if self.choices is not None:
            kwargs['choices_form_class'] = lucky_forms.TypedChoiceField
        else:
            kwargs['widget'] = lucky_forms.CharField.widget
        return super().formfield(**kwargs)
