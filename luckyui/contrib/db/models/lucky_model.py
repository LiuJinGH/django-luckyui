from django.db import models

from .lucky_model_base import LuckyModelBase


class LuckyModel(models.Model, metaclass=LuckyModelBase):
    class Meta:
        # 增加 导入、导出权限
        default_permissions = ("add", "change", "delete", "view", "import", "export")
        abstract = True

    def has_circular_ref(self, super_self, field_name):
        """
        检查是否存在循环引用。
        递归地检查给定字段是否可能导致循环引用。循环引用可能会导致程序崩溃或性能问题，因此需要检测并避免。

        参数:
        super_self - 上层对象，正在被检查的对象。
        field_name - 字段名，用于获取对象的字段值。

        返回值:
        如果存在循环引用，则返回True；否则返回False。
        """
        if super_self == self:
            return True
        super_field = getattr(super_self, field_name)
        if super_field:
            return self.has_circular_ref(super_field, field_name)
        return False
