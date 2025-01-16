from django.forms import widgets


class LuckySelect(widgets.Select):
    template_name = "luckyui/forms/widgets/select.html"
