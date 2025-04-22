from django.forms import fields
from ..widgets import LuckyNumberInput


class IntegerField(fields.IntegerField):
    widget = LuckyNumberInput

    def to_python(self, value):
        from ..widgets import LuckyMoney
        # 需要兼容MoneyField
        if isinstance(self.widget, LuckyMoney):
            value = int(float(value) * 100.0)
            value = super().to_python(value)
            return value
        else:
            return super().to_python(value)
