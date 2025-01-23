from django.contrib.auth.models import Group

from luckyui.contrib.admin import LuckyModelAdmin
from django.contrib import admin

from user.models.lucky_user import LuckyUser


@admin.register(LuckyUser)
class LuckyUserAdmin(LuckyModelAdmin):
    list_display = ['username', 'phone', 'is_staff', 'email', 'date_joined']
    search_fields = ['phone', 'username', 'nickname']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    readonly_fields = ['date_joined', 'last_login']


admin.site.unregister(Group)


@admin.register(Group)
class LuckyGroupAdmin(LuckyModelAdmin):
    list_display = ['name', 'user_num']
    search_fields = ['name']
    filter_horizontal = ("permissions",)

    @admin.display(description='关联用户')
    def user_num(self, obj):
        return str(obj.user_set.count())

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "permissions":
            qs = kwargs.get("queryset", db_field.remote_field.model.objects)
            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            kwargs["queryset"] = qs.select_related("content_type")
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)
