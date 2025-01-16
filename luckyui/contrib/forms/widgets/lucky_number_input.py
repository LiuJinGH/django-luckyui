from django.forms import widgets


class LuckyNumberInput(widgets.NumberInput):
    template_name = "luckyui/forms/widgets/input_number.html"
