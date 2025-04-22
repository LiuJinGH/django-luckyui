from django.forms import widgets
from django.conf import settings
from luckyui.contrib.file_storage.storage import LuckyStorage
from django.core.files.storage import default_storage, FileSystemStorage


class LuckyAsyncImageUpload(widgets.ClearableFileInput):
    template_name = "luckyui/forms/widgets/async_image_upload.html"

    def __init__(self, upload_to=None, *args, **kwargs):
        self.upload_to = upload_to
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value:
            context['widget']['value'] = value.url
        else:
            context['widget']['value'] = ""
        return context

    def value_from_datadict(self, data, files, name):
        """
        在change页面中，点击保存时，会通过这个函数向model form提取field的真实字段值
        :param data:  post请求的data
        :param files: post请求的files
        :param name:  当前字段名
        :return:
        """
        upload = super().value_from_datadict(data, files, name)
        if upload is None and data[name]:
            upload = data[name]
        return upload