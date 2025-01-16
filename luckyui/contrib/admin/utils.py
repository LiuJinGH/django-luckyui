
from django.db import models, router
from django.utils import formats, timezone
from django.utils.hashable import make_hashable
from django.utils.html import format_html
from django.contrib.admin.utils import display_for_value
import json


def display_for_field(value, field, empty_value_display):
    from django.contrib.admin.templatetags.admin_list import _boolean_icon
    from luckyui.contrib.db import fields as lucky_fields

    if getattr(field, "flatchoices", None):
        try:
            return dict(field.flatchoices).get(value, empty_value_display)
        except TypeError:
            # Allow list-like choices.
            flatchoices = make_hashable(field.flatchoices)
            value = make_hashable(value)
            return dict(flatchoices).get(value, empty_value_display)

    # BooleanField needs special-case null-handling, so it comes before the
    # general null test.
    elif isinstance(field, models.BooleanField):
        return _boolean_icon(value)
    elif value is None:
        return empty_value_display
    elif isinstance(field, models.DateTimeField):
        return formats.localize(timezone.template_localtime(value))
    elif isinstance(field, (models.DateField, models.TimeField)):
        return formats.localize(value)
    elif isinstance(field, models.DecimalField):
        return formats.number_format(value, field.decimal_places)
    elif isinstance(field, (models.IntegerField, models.FloatField)):
        # if isinstance(field, lucky_fields.MoneyField):
        #     money = formats.number_format(value / 100, 2)
        #     return str(money) + '元'
        return formats.number_format(value)
    elif isinstance(field, models.FileField) and value:
        if isinstance(field, models.ImageField):
            return format_html('<img class="form-readonly-img" src="{}">', value.url)
        else:
            return format_html('<a href="{}">{}</a>', value.url, value)
    elif isinstance(field, models.JSONField) and value:
        try:
            return json.dumps(value, ensure_ascii=False, cls=field.encoder)
        except TypeError:
            return display_for_value(value, empty_value_display)
    else:
        return display_for_value(value, empty_value_display)
