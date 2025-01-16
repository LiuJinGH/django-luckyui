from django.forms import widgets


class LuckyTextarea(widgets.Textarea):
    template_name = "luckyui/forms/widgets/textarea.html"
