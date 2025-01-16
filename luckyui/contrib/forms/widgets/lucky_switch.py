from django.forms import widgets


class LuckySwitch(widgets.CheckboxInput):
    template_name = "luckyui/forms/widgets/switch.html"
