from import_export.resources import ModelResource
from django.db.models import JSONField
import json


class LuckyModelResource(ModelResource):

    @classmethod
    def field_from_django_field(cls, field_name, django_field, readonly):
        field = super().field_from_django_field(field_name, django_field, readonly)
        # 将列名改成verbose_name
        field.column_name = django_field.verbose_name
        # 将 带有 choices 属性的拉出来
        if hasattr(django_field, 'choices') and django_field.choices:
            field.has_choices = True
        else:
            field.has_choices = False
        if isinstance(django_field, JSONField):
            field.is_json_field = True
        else:
            field.is_json_field = False
        return field

    def export_field(self, field, obj):
        if not obj.id:
            return super().export_field(field, obj)

        field_name = self.get_field_name(field)

        if hasattr(obj, field_name):
            field_value = getattr(obj, field_name)
        else:
            field_value = None

        if getattr(field, 'is_json_field', False) and field_value:
            temp = json.dumps(field_value, ensure_ascii=False)
        elif getattr(field, 'has_choices', False) and field_value:
            # 不应该是 display 会造成导入异常
            # temp = getattr(obj, f"get_{field_name}_display")()
            temp = super().export_field(field, obj)
        else:
            temp = super().export_field(field, obj)
        return temp
