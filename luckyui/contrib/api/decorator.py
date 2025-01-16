import inspect
import sys
import importlib
from django.apps import apps
from django.db import models
from django.urls import path, include
from functools import wraps
from datetime import datetime
from django.utils import timezone

tz = timezone.get_default_timezone()


def lucky_api(function=None, name='', param_str=None, method='post', content_type='json', csrf_exempt=True, is_upload=False):
    def decorator(api_func):
        api_func.name = name
        api_func.method = method
        api_func.content_type = content_type
        api_func.csrf_exempt = csrf_exempt
        api_func.is_upload = is_upload
        api_func.param_str = param_str
        return api_func

    if function is None:
        return decorator
    else:
        return decorator(function)


def auto_include_urls():
    urls = []
    for app in apps.get_app_configs():
        if hasattr(app, 'auto_create_api') and app.auto_create_api:
            app_label = app.name
            api_api_path = app_label + '.api'
            app_api = importlib.import_module(api_api_path)
            urlpatterns = []
            for name, api_class in inspect.getmembers(app_api, inspect.isclass):
                api_obj = api_class()
                for fun_name, api_fun in inspect.getmembers(api_obj, inspect.ismethod):
                    path_name = fun_name
                    if hasattr(api_fun, 'param_str') and api_fun.param_str:
                        path_name = fun_name + api_fun.param_str
                    urlpatterns.append(path(path_name, api_fun, name=fun_name))

            view_path = app_label + '.views'
            app_views = importlib.import_module(view_path)
            for fun_name, view_fun in inspect.getmembers(app_views, inspect.isfunction):
                fun_attr = getattr(app_views, fun_name)
                if view_path in fun_attr.__module__:
                    view_fun_path = 'views/' + fun_name
                    urlpatterns.append(path(view_fun_path, view_fun, name=fun_name))

            app_path = app_label + '/'
            url_path = path(app_path, include(urlpatterns))
            urls.append(url_path)

    return urls


def auto_set_body_model(model, body):
    field_list = model._meta.get_fields()
    for field in field_list:
        name = field.name
        if name not in body:
            continue

        if isinstance(field, models.ImageField):
            continue

        # 基础数据类型
        if isinstance(field, models.CharField) or \
                isinstance(field, models.TextField) or \
                isinstance(field, models.JSONField) or \
                isinstance(field, models.IntegerField) or \
                isinstance(field, models.FloatField) or \
                isinstance(field, models.BooleanField):

            if name in body:
                setattr(model, name, body[name])

        # 时间日期数据类型
        if isinstance(field, models.DateTimeField):

            if name in body and body[name]:
                if body[name].count(':') == 1:
                    datetime_value = datetime.strptime(body[name], '%Y-%m-%d %H:%M')
                else:
                    datetime_value = datetime.strptime(body[name], '%Y-%m-%d %H:%M:%S')
                # datetime_value =  tz.localize(datetime.strptime(body[name], '%Y-%m-%d %H:%M:%S'))

                setattr(model, name, datetime_value)
        elif isinstance(field, models.DateField):

            if name in body and body[name]:
                # datetime_value = tz.localize(datetime.strptime(body[name], '%Y-%m-%d'))
                datetime_value = datetime.strptime(body[name], '%Y-%m-%d')
                setattr(model, name, datetime_value.date())

        elif isinstance(field, models.TimeField):

            if name in body and body[name]:
                # datetime_value = tz.localize(datetime.strptime(body[name], '%H:%M'))
                datetime_value = datetime.strptime(body[name], '%H:%M')
                setattr(model, name, datetime_value.time())

    return model
