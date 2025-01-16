
from django.contrib import admin
from luckyui.contrib.admin import LuckyModelAdmin
from ..models import TestModelFields


@admin.register(TestModelFields)
class TestModelFieldsAdmin(LuckyModelAdmin):
    search_fields = ['char_field']
    list_display = ['char_field', 'switch_field', 'integer_field', 'date_field', 'date_time_field']
    list_filter = ['date_field', 'date_time_field', 'integer_field']

    fieldsets = [
        (
            "基本信息",
            {
                "fields": (
                    ("char_field", "switch_field", "integer_field"),
                    ("date_field", "date_time_field", "image_field"),
                    ("type_choice", "money_field", )
                ),
            },
        )
    ]

