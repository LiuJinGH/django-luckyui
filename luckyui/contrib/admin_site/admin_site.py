import uuid
from django.contrib import admin
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage, FileSystemStorage

from django.http import JsonResponse
from django.urls import path


class LuckyAdminSite(admin.AdminSite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__set_custom_login_form()

    def __set_custom_login_form(self):
        from luckyui.contrib.admin.captcha_forms import CaptchaAdminAuthenticationForm
        self.login_form = CaptchaAdminAuthenticationForm

    @csrf_exempt
    def temp_file_upload(self, request):
        """

        :param request:
        :return:
        """

        if not  request.user.is_authenticated:
            return JsonResponse(data={'msg': '请先登录后使用', 'file_path': None})

        file = request.FILES.get('lucky-async-image')
        name = file.name
        name_type = name.split('.')[-1]
        name = str(uuid.uuid4()) + '.' + name_type

        if isinstance(default_storage, FileSystemStorage):
            file_path = settings.MEDIA_ROOT + f'tmp/{request.user.id}/' + name
        else:
            file_path = f'tmp/{request.user.id}/' + name

        default_storage.save(file_path, file.file)
        file_path = f'tmp/{request.user.id}/' + name
        return JsonResponse(data={'msg': '文件上传成功！', 'file_path': file_path})

    def get_urls(self):

        urlpatterns = super().get_urls()
        temp_file_upload_path = path("temp_file_upload/", self.temp_file_upload, name="temp_file_upload")
        return [temp_file_upload_path] + urlpatterns
