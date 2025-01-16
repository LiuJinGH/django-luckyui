from django.forms import widgets


class LuckyDatePicker(widgets.DateInput):
    template_name = "luckyui/forms/widgets/datepicker.html"

