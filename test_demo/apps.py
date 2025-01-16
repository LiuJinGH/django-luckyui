from django.apps import AppConfig


class TestDemoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_demo'
    verbose_name = '演示应用'
    auto_create_api = True
