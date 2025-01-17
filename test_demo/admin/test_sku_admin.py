
from django.contrib import admin
from luckyui.contrib.admin import LuckyModelAdmin, LuckyTabularInline

from ..models import TestSKU, TestSPU


@admin.register(TestSKU)
class TestSKUAdmin(LuckyModelAdmin):

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        spu_id = request.GET.get('testspu')
        if spu_id:
            initial['spu'] = TestSPU.objects.get(pk=spu_id)
        return initial


class TestSKU_Inline(LuckyTabularInline):
    model = TestSKU
