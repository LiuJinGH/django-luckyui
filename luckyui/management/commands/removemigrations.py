import os
import sys

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '删除migrations文件'

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="app_label",
            nargs="*",
            help="Specify the app label(s) to create migrations for.",
        )

    def handle(self, *app_labels, **options):
        app_labels = set(app_labels)

        # 确认APP是否存在
        app_labels = set(app_labels)
        has_bad_labels = False
        for app_label in app_labels:
            try:
                apps.get_app_config(app_label)
            except LookupError as err:
                self.stderr.write(str(err))
                has_bad_labels = True
        if has_bad_labels:
            sys.exit(2)

        if app_labels:
            for app_label in app_labels:
                self.remove_app(app_label)
        else:
            top_dir = os.getcwd()
            print('top_dir:', top_dir)

    def remove_app(self, app_label):
        path = os.path.join(os.getcwd(), app_label)
        for root, dirs, files in os.walk(path):
            # print('===========')
            # print(root)
            # print(dirs)
            # print(files)
            # print('===========')
            target_path = app_label + '/migrations'
            if target_path in root:
                for file in files:
                    if file == '__init__.py':
                        continue
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
