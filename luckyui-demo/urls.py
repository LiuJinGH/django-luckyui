"""
URL configuration for luckyui-demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls.static import static
from . import ckeditor_views

urlpatterns = [
    path('', lambda r: redirect('admin:index')),
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls'), name='captcha'),
    re_path(r"^ckeditor/upload/", staff_member_required(ckeditor_views.lucky_ck_upload), name="ckeditor_upload"),
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
