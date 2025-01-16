from django.forms import widgets
from .lucky_number_input import LuckyNumberInput


class LuckyMoney(LuckyNumberInput):
    template_name = "luckyui/forms/widgets/input_money.html"
