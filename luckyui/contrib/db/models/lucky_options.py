from django.db.models.options import Options

LUCKY_DEFAULT_NAMES = (
    "view_permissions",
)


class LuckyOptions(Options):

    def __init__(self, meta, app_label=None):
        # 菜单权限
        self.menu_permissions = []
        self.default_menu_permissions = ("default",)
        # 视图权限
        self.view_permissions = []
        self.default_view_permissions = ("add", "change", "delete", "detail", "list")
        # 按钮权限
        self.action_permissions = []
        self.default_action_permissions = ("add", "change", "delete", "view")

        super().__init__(meta, app_label)

    def contribute_to_class(self, cls, name):

        original_attrs = {}
        if self.meta:
            meta_attrs = self.meta.__dict__.copy()

            for attr_name in LUCKY_DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                    original_attrs[attr_name] = getattr(self, attr_name)
                    delattr(self.meta, attr_name)

        super().contribute_to_class(cls, name)
        self.original_attrs.update(original_attrs)
