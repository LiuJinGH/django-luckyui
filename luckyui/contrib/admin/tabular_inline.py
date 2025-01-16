from django.conf import settings
from django import forms
from django.contrib import admin


class LuckyTabularInline(admin.TabularInline):
    rich_text_fields = []
    detail_template = None

    extra = 0
    is_detail_view = False
    show_change_link = True

    enable_el_table = False
    list_display = None

    def __init__(self, parent_model, admin_site):
        super().__init__(parent_model, admin_site)
        if self.enable_el_table:
            self.detail_template = 'admin/edit_inline/el-tabular.html'

    def get_list_display(self, request):
        return self.list_display

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        js = ["vendor/jquery/jquery%s.js" % extra, "jquery.init.js", "inlines.js", "admin/RelatedObjectLookups.js", ]
        if self.filter_vertical or self.filter_horizontal:
            js.extend(["SelectBox.js", "SelectFilter2.js"])
        if self.classes and "collapse" in self.classes:
            js.append("collapse.js")
        return forms.Media(js=["admin/js/%s" % url for url in js])

    def get_readonly_fields(self, request, obj=None):
        path = request.path
        # self.is_detail_view = path[-8:] == '/detail/'
        # if self.is_detail_view:
        readonly_fields = []
        fields = self.opts.fields
        for item in fields:
            readonly_fields.append(item.name)
        return readonly_fields
        # else:
        #     return super().get_readonly_fields(request, obj)
