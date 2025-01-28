import json
from functools import update_wrapper

from django.contrib import admin
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.core.exceptions import PermissionDenied
# select_template 记载模板用的
from django.db import models, router, transaction
from django.template.loader import select_template
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.forms.renderers import get_default_renderer
from django.urls import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.options import TO_FIELD_VAR, IS_POPUP_VAR, get_content_type_for_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin import helpers
from django.utils.translation import gettext as _
from django.forms.formsets import all_valid
from django.contrib.admin.utils import (flatten_fieldsets, quote, unquote, lookup_field, model_format_dict)
from .utils import (display_for_field, )

from simpleui.admin import AjaxAdmin

from luckyui.contrib import helpers as lucky_helpers
from .import_export_mixin import LuckyImportExportMixin

renderer = get_default_renderer()
csrf_protect_m = method_decorator(csrf_protect)


class LuckyModelAdmin(LuckyImportExportMixin, AjaxAdmin):

    def get_view_url(self, view_name, obj=None):
        """
        通过 reverse 方式获取页面URL
        :param view_name:
        :param obj:
        :return:
        """
        app_label = self.opts.app_label
        model_name = self.opts.model_name
        if obj:
            return reverse(
                "admin:%s_%s_%s" % (app_label, model_name, view_name),
                args=(quote(obj.pk),),
                current_app='admin',
            )
        else:
            return reverse(
                "admin:%s_%s_%s" % (app_label, model_name, view_name),
                current_app='admin',
            )

    def get_urls(self, *args, **kwargs):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        # 详情逻辑
        info = self.opts.app_label, self.opts.model_name
        url = [
            path(
                "<path:object_id>/detail/",
                wrap(self.detail_view),
                name="%s_%s_detail" % info,
            )
        ]

        add_urls = []
        for key, value in kwargs.items():  # {url_name:{is_detail:False, add_view: , }}
            info = self.opts.app_label, self.opts.model_name, key
            add_urls.append(
                path(
                    "<path:object_id>/%s/" % key if value.get("is_detail") else key,
                    wrap(value.get("add_view")),
                    name="%s_%s_%s" % info
                )
            )

        return url + add_urls + super().get_urls()

    def get_readonly_fields(self, request, obj=None):
        is_detail_view = self.is_detail_view(request)
        if is_detail_view:
            opts = self.opts
            readonly_list = []
            for field in opts.local_fields:
                readonly_list.append(field.name)
            for field in opts.local_many_to_many:
                readonly_list.append(field.name)
            return readonly_list
        else:
            return super().get_readonly_fields(request, obj=obj)

    def get_inlines(self, request, obj):
        if self.is_detail_view(request):
            return self.inlines
        else:
            return []

    def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
        # Edit permissions on parent model are required for editable inlines.
        can_edit_parent = (
            self.has_change_permission(request, obj)
            if obj
            else self.has_add_permission(request)
        )
        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            if can_edit_parent:
                has_add_permission = inline.has_add_permission(request, obj)
                has_change_permission = inline.has_change_permission(request, obj)
                has_delete_permission = inline.has_delete_permission(request, obj)
            else:
                # Disable all edit-permissions, and override formset settings.
                has_add_permission = (
                    has_change_permission
                ) = has_delete_permission = False
                formset.extra = formset.max_num = 0
            has_view_permission = inline.has_view_permission(request, obj)
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = lucky_helpers.LuckyInlineAdminFormSet(
                inline,
                formset,
                fieldsets,
                prepopulated,
                readonly,
                model_admin=self,
                has_add_permission=has_add_permission,
                has_change_permission=has_change_permission,
                has_delete_permission=has_delete_permission,
                has_view_permission=has_view_permission,
            )
            inline_admin_formsets.append(inline_admin_formset)
        return inline_admin_formsets

    def get_fieldsets(self, request, obj=None):
        """
        兼容详情页的fieldsets
        :param request:
        :param obj:
        :return:
        """
        if self.is_detail_view(request) and self.detail_fieldsets:
            return self.detail_fieldsets
        return super().get_fieldsets(request, obj)

    # ====== 额外字段

    # 富文本字段
    rich_text_fields = []

    # ====== 导入导出 重写 AjaxAdmin ======
    def callback(self, request):
        """
        AjaxAdmin 请求重写，如果是导出文件，无法使用JsonResponse返回。
        :param request:
        :return:
        """
        post = request.POST
        action = post.get("_action")

        if action == 'lucky_export_admin_action' and hasattr(self, action):
            func, action, description = self.get_action(action)
            qs = self._get_queryset(request)
            r = func(self, request, qs)
            return r
        else:
            return super().callback(request)

    def init_change_list_template(self):

        if not getattr(self, "change_list_template", None):
            app_label = self.opts.app_label
            model_label = self.opts.model_name
            template_name = [
                "admin/%s/%s/change_list.html" % (app_label, model_label),
                "admin/%s/change_list.html" % app_label,
                "admin/change_list.html",
            ]
            template_name = select_template(template_name, None)
            template_name = template_name.template.name
            self.change_list_template = template_name
        super().init_change_list_template()

    # ====== 列表页 =======

    # change_list 额外增加的字段
    list_request = None
    item_action_detail_btn = True
    item_action_edit_btn = True
    item_action_list = []
    list_per_page = 20
    list_sizes_page = [10, 20, 50, 100]  # 分页
    list_ignored_params = []  # 列表自定义参数 忽略项

    def get_changelist(self, request, **kwargs):
        """
        改成 LuckyChangeList
        :param request:
        :param kwargs:
        :return:
        """
        from .chang_list import LuckyChangeList
        return LuckyChangeList

    def changelist_view(self, request, extra_context=None):
        """
        重写 changelist_view
        1. 增加列表页字段赋值
        :param request:
        :param extra_context:
        :return:
        """
        self.list_request = request
        return super().changelist_view(request, extra_context)

    def get_list_display(self, request):
        """
        列表页的显示页
        1. 增加 列操作内容
        :param request:
        :return:
        """
        # TODO 需要判断是否要显示item_operate

        # item_operate 是list_display最后一个元素
        if 'item_operate' not in self.list_display:
            if isinstance(self.list_display, tuple):
                self.list_display = self.list_display + ('item_operate',)
            if isinstance(self.list_display, list):
                self.list_display = self.list_display + ['item_operate']

        return super().get_list_display(request)

    def get_action_choices(self, request, default_choices=models.BLANK_CHOICE_DASH):
        choices = [] + default_choices
        self.item_action_list = []
        for func, name, description in self.get_actions(request).values():
            show_in_item = getattr(func, "show_in_item", False)
            in_item_filter = getattr(func, "in_item_filter", [])
            choice = (name, description % model_format_dict(self.opts))
            if show_in_item:
                # 列里面显示
                self.item_action_list.append(choice + (show_in_item, in_item_filter))
            choices.append(choice)
        return choices

    def get_item_action_list(self, obj):
        return self.item_action_list

    def has_item_action(self, obj, item_action):
        return True

    @admin.display(description='操作')
    def item_operate(self, obj, extra_context=None):
        """
        在列表页显示，操作列
        :param obj:
        :param extra_context:
        :return:
        """

        app_label = self.opts.app_label
        renderer = get_default_renderer()
        template_name = [
            "admin/%s/%s/change_list_item_actions.html" % (app_label, self.opts.model_name),
            "admin/%s/change_list_item_actions.html" % app_label,
            "admin/change_list_item_actions.html",
        ]
        template_name = select_template(template_name, None)
        template_name = template_name.template.name

        change_url = self.get_view_url('change', obj)
        detail_url = self.get_view_url('detail', obj)

        item_action_list = []
        for item_action in self.get_item_action_list(obj):
            # 列表级按钮权限控制
            if not self.has_item_action(obj, item_action):
                continue
            item_action_list.append(item_action)

        context = {
            'item_action_detail_btn': self.item_action_detail_btn,
            'item_action_edit_btn': self.item_action_edit_btn,
            'item_action_list': item_action_list,
            'change_url': change_url,
            'detail_url': detail_url,
            'model': obj,
            'user': self.list_request.user
        }

        context.update(extra_context or {})
        return mark_safe(renderer.render(template_name, context))

    # ======= 详情页 =======
    detail_fieldsets = None
    change_request = None
    detail_form_template = None

    def is_detail_view(self, request):
        path = request.path
        return path[-8:] == '/detail/'

    def detail_view(self, request, object_id, form_url="", extra_context=None):
        return self.detailform_view(request, object_id, form_url, extra_context)

    @csrf_protect_m
    def detailform_view(self, request, object_id=None, form_url="", extra_context=None):
        # 事务管理 原子提交
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._detailform_view(request, object_id, form_url, extra_context)

    def _detailform_view(self, request, object_id, form_url, extra_context):
        self.change_request = request

        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        if request.method == "POST" and "_saveasnew" in request.POST:
            object_id = None

        # 详情页没有add功能，待移除
        add = object_id is None
        # 详情页没有add功能，待移除
        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = self.get_object(request, unquote(object_id), to_field)

            if request.method == "POST":
                if not self.has_change_permission(request, obj):
                    raise PermissionDenied
            else:
                if not self.has_view_or_change_permission(request, obj):
                    raise PermissionDenied

            if obj is None:
                return self._get_obj_does_not_exist_redirect(
                    request, self.opts, object_id
                )

        fieldsets = self.get_fieldsets(request, obj)
        ModelForm = self.get_form(
            request, obj, change=not add, fields=flatten_fieldsets(fieldsets)
        )
        # 提交类型的请求
        if request.method == "POST":
            form = ModelForm(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(
                request,
                form.instance,
                change=not add,
            )
            form_validated = form.is_valid()
            if form_validated:
                new_object = self.save_form(request, form, change=not add)
            else:
                new_object = form.instance
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, not add)
                self.save_related(request, form, formsets, not add)
                change_message = self.construct_change_message(
                    request, form, formsets, add
                )
                if add:
                    self.log_addition(request, new_object, change_message)
                    return self.response_add(request, new_object)
                else:
                    self.log_change(request, new_object, change_message)
                    return self.response_change(request, new_object)
            else:
                form_validated = False
        else:
            # 默认指GET请求
            if add:
                initial = self.get_changeform_initial_data(request)
                form = ModelForm(initial=initial)
                formsets, inline_instances = self._create_formsets(
                    request, form.instance, change=False
                )
            else:
                # 自动化字段生成、数据验证
                form = ModelForm(instance=obj)
                formsets, inline_instances = self._create_formsets(
                    request, obj, change=True
                )

                for form_item in formsets:
                    form_item.can_delete = False

        if not add and not self.has_change_permission(request, obj):
            readonly_fields = flatten_fieldsets(fieldsets)
        else:
            readonly_fields = self.get_readonly_fields(request, obj)

        admin_form = lucky_helpers.LuckyAdminForm(
            form,
            list(fieldsets),
            # Clear prepopulated fields on a view-only form to avoid a crash.
            self.get_prepopulated_fields(request, obj)
            if add or self.has_change_permission(request, obj)
            else {},
            readonly_fields,
            model_admin=self,
        )
        media = self.media + admin_form.media
        # formsets inline对应的表单数据
        inline_formsets = self.get_inline_formsets(
            request, formsets, inline_instances, obj
        )

        for inline_formset in inline_formsets:
            media += inline_formset.media

        if add:
            title = _("Add %s")
        elif self.has_change_permission(request, obj):
            title = _("View %s")
        else:
            title = _("View %s")

        # print('is_popup:', (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET))

        context = {
            **self.admin_site.each_context(request),
            "title": title % self.opts.verbose_name,
            "subtitle": str(obj) if obj else None,
            "adminform": admin_form,
            "object_id": object_id,
            "original": obj,
            "is_popup": IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            "to_field": to_field,
            "media": media,
            "inline_admin_formsets": inline_formsets,
            "errors": helpers.AdminErrorList(form, formsets),
            "preserved_filters": self.get_preserved_filters(request),
        }

        # Hide the "Save" and "Save and continue" buttons if "Save as New" was
        # previously chosen to prevent the interface from getting confusing.
        if (
                request.method == "POST"
                and not form_validated
                and "_saveasnew" in request.POST
        ):
            context["show_save"] = False
            context["show_save_and_continue"] = False
            # Use the change template instead of the add template.
            add = False

        context.update(extra_context or {})

        return self.render_detail_form(
            request, context, add=add, change=not add, obj=obj, form_url=form_url
        )

    def render_detail_form(self, request, context, add=False, change=False, form_url="", obj=None):
        app_label = self.opts.app_label
        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters(
            {"preserved_filters": preserved_filters, "opts": self.opts}, form_url
        )
        view_on_site_url = self.get_view_on_site_url(obj)
        has_editable_inline_admin_formsets = False
        for inline in context["inline_admin_formsets"]:
            if (
                    inline.has_add_permission
                    or inline.has_change_permission
                    or inline.has_delete_permission
            ):
                has_editable_inline_admin_formsets = True
                break
        context.update(
            {
                "add": add,
                "change": change,
                "has_view_permission": self.has_view_permission(request, obj),
                "has_add_permission": self.has_add_permission(request),
                "has_change_permission": self.has_change_permission(request, obj),
                "has_delete_permission": self.has_delete_permission(request, obj),
                "has_editable_inline_admin_formsets": (
                    has_editable_inline_admin_formsets
                ),
                "has_file_field": context["adminform"].form.is_multipart()
                                  or any(
                    admin_formset.formset.is_multipart()
                    for admin_formset in context["inline_admin_formsets"]
                ),
                "has_absolute_url": view_on_site_url is not None,
                "absolute_url": view_on_site_url,
                "form_url": form_url,
                "opts": self.opts,
                "content_type_id": get_content_type_for_model(self.model).pk,
                "save_as": self.save_as,
                "save_on_top": self.save_on_top,
                "to_field_var": TO_FIELD_VAR,
                "is_popup_var": IS_POPUP_VAR,
                "app_label": app_label,
            }
        )
        if add and self.add_form_template is not None:
            form_template = self.add_form_template
        else:
            form_template = self.detail_form_template

        request.current_app = self.admin_site.name

        # model对象的字段名：original

        return TemplateResponse(
            request,
            form_template
            or [
                "admin/%s/%s/detail_form.html" % (app_label, self.opts.model_name),
                "admin/%s/detail_form.html" % app_label,
                "admin/detail_form.html",
            ],
            context,
        )

    def _changeform_view(self, request, object_id, form_url, extra_context):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                "The field %s cannot be referenced." % to_field
            )

        if request.method == "POST" and "_saveasnew" in request.POST:
            object_id = None

        add = object_id is None

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = self.get_object(request, unquote(object_id), to_field)

            if request.method == "POST":
                if not self.has_change_permission(request, obj):
                    raise PermissionDenied
            else:
                if not self.has_view_or_change_permission(request, obj):
                    raise PermissionDenied

            if obj is None:
                return self._get_obj_does_not_exist_redirect(
                    request, self.opts, object_id
                )

        fieldsets = self.get_fieldsets(request, obj)
        ModelForm = self.get_form(
            request, obj, change=not add, fields=flatten_fieldsets(fieldsets)
        )
        if request.method == "POST":
            form = ModelForm(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(
                request,
                form.instance,
                change=not add,
            )
            form_validated = form.is_valid()
            if form_validated:
                new_object = self.save_form(request, form, change=not add)
            else:
                new_object = form.instance
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, not add)
                self.save_related(request, form, formsets, not add)
                change_message = self.construct_change_message(
                    request, form, formsets, add
                )
                if add:
                    self.log_addition(request, new_object, change_message)
                    return self.response_add(request, new_object)
                else:
                    self.log_change(request, new_object, change_message)
                    return self.response_change(request, new_object)
            else:
                form_validated = False
        else:
            if add:
                initial = self.get_changeform_initial_data(request)
                form = ModelForm(initial=initial)
                formsets, inline_instances = self._create_formsets(
                    request, form.instance, change=False
                )
            else:
                form = ModelForm(instance=obj)
                formsets, inline_instances = self._create_formsets(
                    request, obj, change=True
                )

        if not add and not self.has_change_permission(request, obj):
            readonly_fields = flatten_fieldsets(fieldsets)
        else:
            readonly_fields = self.get_readonly_fields(request, obj)
        admin_form = lucky_helpers.LuckyAdminForm(
            form,
            list(fieldsets),
            # Clear prepopulated fields on a view-only form to avoid a crash.
            self.get_prepopulated_fields(request, obj)
            if add or self.has_change_permission(request, obj)
            else {},
            readonly_fields,
            model_admin=self,
        )
        media = self.media + admin_form.media

        inline_formsets = self.get_inline_formsets(
            request, formsets, inline_instances, obj
        )
        for inline_formset in inline_formsets:
            media += inline_formset.media

        if add:
            title = _("Add %s")
        elif self.has_change_permission(request, obj):
            title = _("Change %s")
        else:
            title = _("View %s")
        context = {
            **self.admin_site.each_context(request),
            "title": title % self.opts.verbose_name,
            "subtitle": str(obj) if obj else None,
            "adminform": admin_form,
            "object_id": object_id,
            "original": obj,
            "is_popup": IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            "to_field": to_field,
            "media": media,
            "inline_admin_formsets": inline_formsets,
            "errors": helpers.AdminErrorList(form, formsets),
            "preserved_filters": self.get_preserved_filters(request),
        }

        # Hide the "Save" and "Save and continue" buttons if "Save as New" was
        # previously chosen to prevent the interface from getting confusing.
        if (
                request.method == "POST"
                and not form_validated
                and "_saveasnew" in request.POST
        ):
            context["show_save"] = False
            context["show_save_and_continue"] = False
            # Use the change template instead of the add template.
            add = False

        context.update(extra_context or {})

        return self.render_change_form(
            request, context, add=add, change=not add, obj=obj, form_url=form_url
        )


