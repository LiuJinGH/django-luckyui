from django.contrib import admin
from django.http import HttpResponse

from import_export.resources import modelresource_factory
from import_export.admin import ImportExportMixin

from .model_resource import LuckyModelResource


class LuckyImportExportMixin(ImportExportMixin):
    resource_class = LuckyModelResource

    def get_resource_classes(self):
        return [modelresource_factory(self.model, resource_class=self.resource_class)]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if hasattr(self, 'resource_class') and self.has_export_permission(request):
            actions.update(
                lucky_export_admin_action=(
                    self.lucky_export_admin_action,
                    "lucky_export_admin_action",
                    "导出",
                )
            )
        return actions

    @admin.action()
    def lucky_export_admin_action(self, request, queryset):
        """
            处理导出事件
        :param request:
        :param queryset:
        :return:
        """
        post = request.POST

        formats = self.get_export_formats()
        file_format = formats[int(post.get('file_type'))]()

        export_data = self.get_export_data(file_format, queryset, request=request, encoding=self.to_encoding)
        content_type = file_format.get_content_type()
        response = HttpResponse(export_data, content_type=content_type)
        filename = self.get_export_filename(request, queryset, file_format)
        response['filename'] = filename
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename,)
        return response

    lucky_export_admin_action.layer = {
        'title': '导出',
        'tips': '一次性导出大量数据会导致卡顿！',
        'confirm_button': '确认',
        'cancel_button': '取消',
        'labelWidth': '100px',
        'params': [

            {
                'type': 'select',
                'key': 'file_type',
                'label': '文件类型',
                'value': '0',
                'size': 'small',
                'not_search': True,
                'options': [
                    {
                        'key': '0',
                        'label': 'csv'
                    }, {
                        'key': '1',
                        'label': 'xls'
                    }, {
                        'key': '2',
                        'label': 'xlsx'
                    }, {
                        'key': '3',
                        'label': 'tsv'
                    }, {
                        'key': '4',
                        'label': 'ods'
                    }, {
                        'key': '5',
                        'label': 'json'
                    }, {
                        'key': '6',
                        'label': 'yaml'
                    }, {
                        'key': '7',
                        'label': 'html'
                    }
                ]
            }, {
                'type': 'radio',
                'key': 'filter_type',
                'label': '导出范围',
                'value': '0',
                'size': 'small',
                'options': [

                    {
                        'key': '0',
                        'label': '导出所有'
                    }, {
                        'key': '1',
                        'label': '仅导出选择项'
                    }, {
                        'key': '2',
                        'label': '仅导出搜索结果'
                    },
                ]
            }
        ]
    }
