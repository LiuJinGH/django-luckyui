import json
import os
import sys
import importlib
import inspect

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '生成接口JSON文件'

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="app_label",
            nargs="*",
            help="Specify the app label(s) to create migrations for.",
        )

    def handle(self, *app_labels, **options):
        app_labels = set(app_labels)

        if len(app_labels) == 0:
            app_list = []
            for app in apps.get_app_configs():
                if hasattr(app, 'auto_create_api') and app.auto_create_api:
                    app_list.append(app.name)
                    print(app.name)
            app_labels = app_list

        for app in app_labels:
            self.create_app_api(app)

    def create_app_api(self, app_label):
        api_api_path = app_label + '.api'
        app_api = importlib.import_module(api_api_path)

        api_json = []

        for name, api_class in inspect.getmembers(app_api, inspect.isclass):

            for fun_name, api_fun in inspect.getmembers(api_class, inspect.isfunction):
                api_json.append({
                    'api': fun_name,
                    'name': api_fun.name,
                    'method': api_fun.method,
                    'content_type': api_fun.content_type,
                    'is_upload': api_fun.is_upload
                })
        json_path = app_label + '/api/' + app_label + '_api.js'
        self.create_api_js(app_label, json_path, api_json)

    def create_api_js(self, app_label, js_path, api_json):
        js_path = os.path.join(os.getcwd(), js_path)
        if os.path.exists(js_path):
            os.remove(js_path)

        with open(js_path, "w") as js_file:
            js_file.write('import request from "@/common/app_request.js"\n')
            js_file.write('const app = "{}"\n\n'.format(app_label))

            for api_item in api_json:
                # 减少js体积，去掉注释
                # js_file.write('/* {} */\n'.format(api_item['name']))
                js_file.write('function %s(param){\n' % api_item['api'])
                js_file.write('\tparam.api = "/" + app + "/{}"\n'.format(api_item['api']))
                # 减少js体积，去掉注释
                # js_file.write('\tparam.name = "{}"\n'.format(api_item['name']))
                if api_item['is_upload']:
                    js_file.write('\tif(param.filePath){\n')
                    js_file.write('\t\trequest.upload(param)\n')
                    js_file.write('\t}else{\n')
                    js_file.write('\t\trequest.post_json_request(param)\n')
                    js_file.write('\t}\n')
                else:
                    js_file.write('\treturn request.post_json_request(param)\n')
                js_file.write('}\n\n')

            js_file.write('export default {\n')
            for api_item in api_json:
                js_file.write('\t{},\n'.format(api_item['api']))
            js_file.write('}')
