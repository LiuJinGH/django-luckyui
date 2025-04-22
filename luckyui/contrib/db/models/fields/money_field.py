
from .interger_field import IntegerField
from luckyui.contrib.forms.widgets import LuckyMoney


class MoneyField(IntegerField):

    def formfield(self, **kwargs):
        kwargs['widget'] = LuckyMoney
        formfield = super().formfield(**kwargs)
        return formfield

    def to_python(self, value):
        if value is None:
            return value
        return round(value / 100.0, 2)

    def get_prep_value(self, value):
        if value is None:
            return value
        return int(value * 100)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.to_python(value)
