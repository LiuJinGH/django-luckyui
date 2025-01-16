from django.forms import widgets


class LuckyFileUpload(widgets.ClearableFileInput):
    template_name = "luckyui/forms/widgets/image_upload.html"
