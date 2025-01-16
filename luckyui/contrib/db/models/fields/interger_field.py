from django.db.models import fields
from luckyui.contrib import forms as lucky_forms
from luckyui.contrib.forms import LuckyNumberInput


class IntegerField(fields.IntegerField):

    def formfield(self, **kwargs):

        kwargs['form_class'] = lucky_forms.IntegerField
        if self.choices is not None:
            kwargs['choices_form_class'] = lucky_forms.TypedChoiceField
        elif 'widget' not in kwargs or not issubclass(kwargs['widget'], LuckyNumberInput):
            kwargs['widget'] = LuckyNumberInput
        return super().formfield(**kwargs)
