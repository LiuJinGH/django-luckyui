from django.conf import settings
from django.core.files.storage import default_storage, FileSystemStorage
from django.db.models import fields
from django.db.models.fields import files

from luckyui.contrib.file_storage.storage import LuckyStorage
from luckyui.contrib import forms as lucky_forms


class AsyncImageFieldDescriptor(files.ImageFileDescriptor):

    def __get__(self, instance, cls=None):
        return super().__get__(instance, cls)

    def __set__(self, instance, value):
        instance.__dict__[self.field.attname] = value

class AsyncImageField(fields.CharField):
    attr_class = files.ImageFieldFile
    descriptor_class = AsyncImageFieldDescriptor

    def __init__(self, *args, upload_to='', storage=default_storage,  **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 150
        self.upload_to = upload_to
        self.storage = storage
        super().__init__(*args, **kwargs)

    def display_value(self, value):
        image_path = self.storage.url(value)
        return image_path

    def save_form_data(self, instance, data):

        # 将临时文件转到 upload_to 目录中
        if 'tmp/' in data:

            if isinstance(default_storage, FileSystemStorage):
                old_path = settings.MEDIA_ROOT + data
                new_path = settings.MEDIA_ROOT + self.upload_to + data.split('/')[-1]
            else:
                old_path = data
                new_path = self.upload_to + data.split('/')[-1]

            if default_storage.exists(old_path):
                data = new_path

                if isinstance(default_storage, FileSystemStorage):
                    file = default_storage.open(old_path)
                    default_storage.save(new_path, file.file)
                    default_storage.delete(old_path)

                if isinstance(default_storage, LuckyStorage):
                    default_storage.move(old_path, new_path)

        # 将旧数据移除
        old_data = getattr(instance, self.name)
        old_data = old_data.name
        if data != old_data:
            # 删除旧数据
            if old_data:
                if isinstance(default_storage, FileSystemStorage):
                    old_path = settings.MEDIA_ROOT + old_data
                else:
                    old_path = old_data

                if default_storage.exists(old_path):
                    default_storage.delete(old_path)
        super().save_form_data(instance, data)

    def formfield(self, **kwargs,):
        kwargs['widget'] = lucky_forms.LuckyAsyncImageUpload(upload_to=self.upload_to)
        return super().formfield(**kwargs)
