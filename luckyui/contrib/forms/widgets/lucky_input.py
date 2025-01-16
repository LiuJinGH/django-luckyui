from django.forms import widgets


class LuckyInput(widgets.TextInput):
    template_name = "luckyui/forms/widgets/input.html"
