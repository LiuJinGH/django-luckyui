import json
import re
from django.urls import NoReverseMatch, reverse
from django.contrib.admin import helpers
from django.template.defaultfilters import capfirst, linebreaksbr
from django.utils.html import conditional_escape, format_html
from luckyui.contrib.utils import display_for_field
from django.core.exceptions import ObjectDoesNotExist, FieldDoesNotExist
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from django.db.models.fields.related import (
    ForeignObjectRel,
    ManyToManyRel,
    OneToOneField,
)

from django.contrib.admin.utils import (
    lookup_field,
    quote,
    flatten_fieldsets,
    label_for_field,
    help_text_for_field,
)

from luckyui.contrib import utils as lucky_utils


class LuckyAdminForm(helpers.AdminForm):

    def __iter__(self):
        for name, options in self.fieldsets:
            yield LuckyFieldset(
                self.form,
                name,
                readonly_fields=self.readonly_fields,
                model_admin=self.model_admin,
                **options,
            )


class LuckyFieldset(helpers.Fieldset):

    def __iter__(self):
        for field in self.fields:
            yield LuckyFieldline(
                self.form, field, self.readonly_fields, model_admin=self.model_admin
            )


class LuckyFieldline(helpers.Fieldline):

    def __iter__(self):
        for i, field in enumerate(self.fields):
            if field in self.readonly_fields:
                yield LuckyAdminReadonlyField(
                    self.form, field, is_first=(i == 0), model_admin=self.model_admin
                )
            else:
                yield LuckyAdminField(self.form, field, is_first=(i == 0))


class LuckyAdminField(helpers.AdminField):

    def label_tag(self):
        classes = []
        contents = conditional_escape(self.field.label)
        if self.is_checkbox:
            classes.append("vCheckboxLabel")

        if self.field.field.required:
            classes.append("required")
        if not self.is_first:
            classes.append("inline")
        attrs = {"class": " ".join(classes)} if classes else {}
        # checkboxes should not have a label suffix as the checkbox appears
        # to the left of the label.
        return self.field.label_tag(
            contents=mark_safe(contents),
            attrs=attrs,
            label_suffix=":"
        )


class LuckyAdminReadonlyField(helpers.AdminReadonlyField):

    def __init__(self, form, field, is_first, model_admin=None):
        self.is_richtext = False
        self.is_iframe = False
        super().__init__(form, field, is_first, model_admin)

        try:
            f, attr, value = lookup_field(self.field["field"], self.form.instance, self.model_admin)
        except (AttributeError, ValueError, ObjectDoesNotExist):
            pass
        else:
            try:
                from ckeditor_uploader.fields import RichTextUploadingField
                if isinstance(f, RichTextUploadingField):
                    self.is_richtext = True
            except ImportError:
                self.is_richtext = False

        if field in model_admin.rich_text_fields:
            self.is_richtext = True
            f, attr, value = lookup_field(self.field["field"], self.form.instance, self.model_admin)
            if "b'<!DOCTYPE html>" in value:
                self.is_iframe = True

    def contents(self):
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        field, obj, model_admin = (
            self.field["field"],
            self.form.instance,
            self.model_admin,
        )
        try:
            f, attr, value = lookup_field(field, obj, model_admin)
        except (AttributeError, ValueError, ObjectDoesNotExist):
            result_repr = self.empty_value_display
        else:
            if self.is_iframe:
                byte_string = eval(value)
                value = byte_string.decode('utf-8')
                value = re.sub(r"\n", "", value)
            if field in self.form.fields:
                widget = self.form[field].field.widget
                # This isn't elegant but suffices for contrib.auth's
                # ReadOnlyPasswordHashWidget.
                if getattr(widget, "read_only", False):
                    return widget.render(field, value)
            if f is None:
                if getattr(attr, "boolean", False):
                    result_repr = _boolean_icon(value)
                else:
                    if hasattr(value, "__html__"):
                        result_repr = value
                    else:
                        result_repr = linebreaksbr(value)
            else:
                if isinstance(f.remote_field, ManyToManyRel) and value is not None:
                    result_repr = ", ".join(map(str, value.all()))
                elif (
                        isinstance(f.remote_field, (ForeignObjectRel, OneToOneField))
                        and value is not None
                ):
                    result_repr = self.get_admin_url(f.remote_field, value)
                else:
                    result_repr = display_for_field(value, f, self.empty_value_display)
                # 去掉 所有的<a>标签
                if isinstance(self.model_admin, admin.options.InlineModelAdmin) and isinstance(f, models.ForeignKey):
                    result_repr = value
                result_repr = linebreaksbr(result_repr)
        return conditional_escape(result_repr)

    # 详情页默认链接跳转
    def get_admin_url(self, remote_field, remote_obj):
        url_name = "admin:%s_%s_detail" % (
            remote_field.model._meta.app_label,
            remote_field.model._meta.model_name,
        )
        try:
            url = reverse(
                url_name,
                args=[quote(remote_obj.pk)],
                current_app=self.model_admin.admin_site.name,
            )
            return format_html('<a class="readonly_admin_url_a" href="{}">{}</a>', url, remote_obj)

        except NoReverseMatch:
            return str(remote_obj)


class LuckyInlineAdminFormSet(helpers.InlineAdminFormSet):
    table_data = None
    table_column = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_table_data()

    def __iter__(self):
        if self.has_change_permission:
            readonly_fields_for_editing = self.readonly_fields
        else:
            readonly_fields_for_editing = self.readonly_fields + flatten_fieldsets(
                self.fieldsets
            )

        for form, original in zip(
                self.formset.initial_forms, self.formset.get_queryset()
        ):
            view_on_site_url = self.opts.get_view_on_site_url(original)
            yield LuckyInlineAdminForm(
                self.formset,
                form,
                self.fieldsets,
                self.prepopulated_fields,
                original,
                readonly_fields_for_editing,
                model_admin=self.opts,
                view_on_site_url=view_on_site_url,
            )
        for form in self.formset.extra_forms:
            yield LuckyInlineAdminForm(
                self.formset,
                form,
                self.fieldsets,
                self.prepopulated_fields,
                None,
                self.readonly_fields,
                model_admin=self.opts,
            )
        if self.has_add_permission:
            yield LuckyInlineAdminForm(
                self.formset,
                self.formset.empty_form,
                self.fieldsets,
                self.prepopulated_fields,
                None,
                self.readonly_fields,
                model_admin=self.opts,
            )

    def setup_table_data(self):
        inline = self.opts
        model_admin = self.model_admin
        request = model_admin.change_request
        model = inline.model
        if inline.enable_el_table:
            # inline 激活 el表格 opts就是inline
            tab_column = []
            tab_data = []
            # 头数据
            for field_name in inline.get_list_display(request):
                # print(field_name)
                tab_col_item = {
                    'key': field_name,
                    'label': '',
                    'fun': None,
                    'field': None
                }
                try:
                    # 判断 field_name 是否在model的字段里面
                    field = model._meta.get_field(field_name)
                except FieldDoesNotExist as err:
                    # 判断 field_name 是否是函数
                    field_fun = getattr(inline, field_name)
                    tab_col_item['fun'] = field_fun
                    tab_col_item['label'] = field_fun.short_description
                else:
                    tab_col_item['field'] = field
                    tab_col_item['label'] = field.verbose_name
                tab_column.append(tab_col_item)
            self.table_column = tab_column

            # 表数据
            for form_item in self.forms:
                obj = form_item.instance
                change_url = reverse('admin:%s_%s_change' % (model._meta.app_label, model._meta.model_name),
                                     args=[obj.id])
                detail_url = reverse('admin:%s_%s_detail' % (model._meta.app_label, model._meta.model_name),
                                     args=[obj.id])
                delete_url = reverse('admin:%s_%s_delete' % (model._meta.app_label, model._meta.model_name),
                                     args=[obj.id]) + '?_to_field=id&_popup=1'
                tab_item = {
                    'id': obj.id,
                    'change_url': change_url if self.has_change_permission else None,
                    'detail_url': detail_url if self.has_view_permission else None,
                    'delete_url': delete_url if self.has_delete_permission else None
                }
                for col_item in self.table_column:
                    if col_item['fun']:
                        tab_item[col_item['key']] = col_item['fun'](obj)
                    else:
                        value = getattr(obj, col_item['key'])
                        tab_item[col_item['key']] = lucky_utils.display_for_field(value, col_item['field'], '-')
                tab_data.append(tab_item)

            self.table_data = tab_data


class LuckyInlineAdminForm(helpers.InlineAdminForm):

    def __iter__(self):
        for name, options in self.fieldsets:
            yield LuckyInlineFieldset(
                self.formset,
                self.form,
                name,
                self.readonly_fields,
                model_admin=self.model_admin,
                **options,
            )


class LuckyInlineFieldset(helpers.InlineFieldset):

    def __iter__(self):
        fk = getattr(self.formset, "fk", None)
        for field in self.fields:
            if not fk or fk.name != field:
                yield LuckyFieldline(
                    self.form, field, self.readonly_fields, model_admin=self.model_admin
                )
