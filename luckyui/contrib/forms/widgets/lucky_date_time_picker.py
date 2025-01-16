from django.forms import widgets


class LuckyDateTimePicker(widgets.SplitDateTimeWidget):
    template_name = "luckyui/forms/widgets/datetimepicker.html"

