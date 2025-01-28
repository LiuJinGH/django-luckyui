import json

from django import forms


class LuckyCascader(forms.Widget):
    template_name = "luckyui/forms/widgets/cascader.html"

    def __init__(self, attrs=None, cascader_options=None):
        if cascader_options is None:
            cascader_options = []
        self.cascader_options = cascader_options
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['cascader_options'] = json.dumps(self.cascader_options)
        return context
