import json
import os
import sys
import importlib
import inspect
from django.db import models
from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '获取IntegerChoices数据'

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="app_label",
            nargs="*",
            help="Specify the app label(s) to create migrations for.",
        )

    def handle(self, *app_labels, **options):

        integer_choices = []
        for app in apps.get_app_configs():
            if hasattr(app, 'auto_create_api') and app.auto_create_api:
                models_module = __import__(f"{app.name}.models", fromlist=[''])
                for model_name in dir(models_module):
                    model = getattr(models_module, model_name)
                    if isinstance(model, type) and issubclass(model, models.IntegerChoices):
                        integer_choices.append(model)

        integer_fields = []
        error_count = 0
        error_app_list = []
        for app in apps.get_app_configs():
            for model in app.get_models():
                if hasattr(app, 'auto_create_api') and app.auto_create_api:
                    # 遍历模型的每个字段
                    for field in model._meta.fields:
                        if isinstance(field, models.IntegerField) and hasattr(field, 'choices') and field.choices:
                            field_list = field.choices
                            model_name = model.__name__.lower()
                            choice_dic = self.get_field_choices_list(integer_choices, field_list)
                            if not choice_dic:
                                error_count += 1
                                error_app_list.append({"app": app.label, "model": model_name, "field": field.name})
                            item = {
                                "app": app.label,
                                "model": model_name,
                                "field": field.name,
                                "choice_dic": choice_dic
                            }
                            integer_fields.append(item)

        with open('dic_json.json', "w", encoding='utf-8') as js_file:
            js_file.write(json.dumps(integer_fields, indent=4, ensure_ascii=False))
        print(error_count)

    def get_field_choices_list(self, integer_choices, choice_dic):
        for app_model in integer_choices:
            check_dic = []
            return_dic = []
            for member in app_model:
                item = {
                    'key': member.name,
                    "value": member.value,
                    "remark": str(member.label)
                }
                return_dic.append(item)
                check_dic.append((member.value, member.label))
            if check_dic == choice_dic:
                return return_dic

        return None

    # def get_models_use(self, model_name, check_dic):
    #     path = []
    #     for app in apps.get_app_configs():
    #         for model in app.
    #         ():
    #             if hasattr(app, 'auto_create_api') and app.auto_create_api:
    #                 # 遍历模型的每个字段
    #                 for field in model._meta.fields:
    #                     if isinstance(field, models.IntegerField) and hasattr(field, 'choices') and field.choices:
    #                         class_name = field.default.__class__.__name__
    #                         field_list = field.choices
    #                         if field_list == check_dic:
    #                             app = app.__module__.split('.')[0]
    #                             model = model.__name__
    #                             item = {
    #                                 'app': app,
    #                                 'model': model,
    #                                 'field': field.name
    #                             }
    #                             path.append(item)
    #     return path
