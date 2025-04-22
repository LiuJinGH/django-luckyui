from django.forms import widgets


class LuckyImageListUpload(widgets.ClearableFileInput):
    template_name = "luckyui/forms/widgets/async_image_list_upload.html"

    def __init__(self, upload_to=None, *args, **kwargs):
        self.upload_to = upload_to
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        return context

