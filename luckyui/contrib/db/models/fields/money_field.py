
from .interger_field import IntegerField
from luckyui.contrib.forms.widgets import LuckyMoney


class MoneyField(IntegerField):

    def formfield(self, **kwargs):
        kwargs['widget'] = LuckyMoney
        formfield = super().formfield(**kwargs)
        return formfield
