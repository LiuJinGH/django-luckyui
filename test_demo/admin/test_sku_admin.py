
from django.contrib import admin
from luckyui.contrib.admin import LuckyModelAdmin, LuckyTabularInline

from ..models import TestSKU


@admin.register(TestSKU)
class TestSKUAdmin(LuckyModelAdmin):
    pass


class TestSKU_Inline(LuckyTabularInline):
    model = TestSKU
