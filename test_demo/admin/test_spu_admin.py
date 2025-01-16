
from django.contrib import admin
from django.contrib import messages

from luckyui.contrib.admin import LuckyModelAdmin

from ..models import TestSPU
from .test_sku_admin import TestSKU_Inline


@admin.register(TestSPU)
class TestSPUAdmin(LuckyModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'sku_num']
    inlines = [TestSKU_Inline]
    rich_text_fields = ['detail']
    actions = ['publish_spu']

    fieldsets = [
        ('基本信息', {'fields': ('name', 'detail'),})
    ]

    detail_fieldsets = [
        ('基本信息', {'fields': ('name',),})
    ]

    @admin.display(description='SKU数量')
    def sku_num(self, obj):
        return obj.testsku_set.count()

    @admin.action(description='上架')
    def publish_spu(self, request, queryset):
        self.message_user(request, '已经成功下架商品', messages.SUCCESS)

    publish_spu.show_in_item = True
    publish_spu.type = 'text'
