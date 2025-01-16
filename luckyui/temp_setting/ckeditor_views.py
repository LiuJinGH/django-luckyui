import json
import uuid

from ckeditor_uploader.views import ImageUploadView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator


def generator_filename(filename, request):
    file_type = filename.split('.')[-1]
    file_name = uuid.uuid4().hex + '.' + file_type
    return file_name


class LuckyImageUploadView(ImageUploadView):

    def post(self, request, **kwargs):
        response = super().post(request, **kwargs)
        if isinstance(response, JsonResponse):
            res_data = json.loads(response.content)
            res_data['width'] = '100%'
            res_data['height'] = 'auto'
            response.content = json.dumps(res_data)
        return response


lucky_ck_upload = csrf_exempt(LuckyImageUploadView.as_view())
