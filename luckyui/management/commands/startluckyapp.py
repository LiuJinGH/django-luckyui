import os

from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand


class Command(TemplateCommand):
    help = '创建基于LuckyUI的APP'
    missing_args_message = "你需要提供APP名称。"

    def handle(self, **options):

        app_name = options.pop("name")
        target = options.pop("directory")
        super().handle("app", app_name, target, **options)

        if target is None:
            top_dir = os.path.join(os.getcwd(), app_name)
        else:
            top_dir = os.path.abspath(os.path.expanduser(target))

        self.make_subdir('api', top_dir)
        self.make_subdir('admin', top_dir)
        self.make_subdir('models', top_dir)
        self.make_subdir('service', top_dir)
        self.make_subdir('tests', top_dir)

        # 删除文件
        test_py = os.path.join(top_dir, 'tests.py')
        admin_py = os.path.join(top_dir, 'admin.py')
        models_py = os.path.join(top_dir, 'models.py')
        os.remove(test_py)
        os.remove(admin_py)
        os.remove(models_py)

        # 创建文件
        urls_py = os.path.join(top_dir, "urls.py")
        open(urls_py, 'a').close()
        res_map_py = os.path.join(top_dir, "res_map.py")
        open(res_map_py, 'a').close()

        app_py = os.path.join(top_dir, 'apps.py')
        if os.path.exists(app_py):
            with open(app_py, "a") as f:
                verbose_name = "    verbose_name = '%s'" % app_name
                f.write(verbose_name)
                f.write('\n')
                auto_create_api = "    auto_create_api = True"
                f.write(auto_create_api)
                f.write('\n')

    def make_subdir(self, dir_name, top_dir):
        dir_path = os.path.join(top_dir, dir_name)
        os.makedirs(dir_path)
        init_py = os.path.join(dir_path, "__init__.py")
        open(init_py, 'a').close()
