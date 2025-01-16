import uuid

from luckyui.contrib import forms as lucky_forms
from django.db.models.fields import files


class ImageField(files.ImageField):

    def generate_filename(self, instance, filename):
        """
        生成文件名
        1. 将图片名转码
        """
        file_type = ''
        if '.' in filename:
            file_type = filename.split('.')[-1]
        uuid_value = str(uuid.uuid4()).replace('-', '')
        uuid_value = uuid_value + '.' + file_type
        return super().generate_filename(instance, uuid_value)

    def formfield(self, **kwargs):
        kwargs['form_class'] = lucky_forms.ImageField
        kwargs['widget'] = lucky_forms.ImageField.widget

        temp = super().formfield(**kwargs)

        return temp
