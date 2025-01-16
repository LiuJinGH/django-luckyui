from django.urls import NoReverseMatch
from django.contrib.admin.views.main import ChangeList

SIZE_VAR = "s"
IGNORED_PARAMS = (SIZE_VAR,)


class LuckyChangeList(ChangeList):

    def __init__(self,  request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields,
                 list_select_related, list_per_page, list_max_show_all, list_editable, model_admin, sortable_by,
                 search_help_text, ):
        if model_admin.list_sizes_page:
            self.list_sizes_page = model_admin.list_sizes_page

        self.params = dict(request.GET.items())
        if SIZE_VAR in self.params:
            list_per_page = int(self.params[SIZE_VAR])
            del self.params[SIZE_VAR]

        super().__init__(request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields,
                         list_select_related, list_per_page, list_max_show_all, list_editable, model_admin, sortable_by,
                         search_help_text)

    def get_filters_params(self, params=None):
        params = params or self.params
        lookup_params = params.copy()
        for ignored in IGNORED_PARAMS:
            if ignored in lookup_params:
                del lookup_params[ignored]
                # 理解了，这里不删，super会继续把ignored掉的加回去
                del self.params[ignored]
        for ignored in self.model_admin.list_ignored_params:
            if ignored in lookup_params:
                del lookup_params[ignored]
                del self.params[ignored]
        return super().get_filters_params(lookup_params)

    def url_for_result(self, result):
        # 这里不希望在列表页出现跳转a标签
        raise NoReverseMatch("luckyui：此处不希望在列表页出现跳转a标签")
