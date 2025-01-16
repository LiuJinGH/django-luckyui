import json
from collections import defaultdict
from django import template
from simpleui.templatetags.simpletags import LazyEncoder

register = template.Library()


@register.simple_tag(takes_context=True)
def list_widget_optgroups(context):
    widget_optgroups = context['widget']['optgroups']
    option_list = []
    for item in widget_optgroups:
        if item[1][0]:
            option_list.append(item[1][0]['value'].instance)

    option_app_label_list = []
    option_item_list = []
    content_id_list = []

    for option in option_list:
        content_type_id = str(option.content_type_id) + "lucky_role"
        if option.content_type is None:
            app_label_id = "未知应用"
            app_label_name = "未知应用"
        else:
            app_label_id = option.content_type.app_label
            app_label_name = option.content_type.name

        option_json = {
            'id': option.id,
            'content_type_id': content_type_id,
            'label': option.name,
            'app_label': app_label_id,
        }
        if app_label_id in option_app_label_list:
            app_label_index = option_app_label_list.index(app_label_id)
            for index, content_type in enumerate(content_id_list):
                if app_label_id == content_type['id']:
                    if content_type_id in content_type['option']:
                        option_type_index = content_type['option'].index(content_type_id)
                        option_item_list[app_label_index]['children'][option_type_index]['children'].append(option_json)
                        break
                    else:
                        option_item_list[app_label_index]['children'].append({
                            "id": content_type_id,
                            "label": app_label_name,
                            "children": [option_json]
                        })
                        content_id_list[index]['option'].append(content_type_id)
                        break
                else:
                    continue
        else:
            option_item_list.append({
                "id": app_label_id,
                "label": app_label_id,
                "children": [{
                    "id": content_type_id,
                    "label": app_label_name,
                    "children": [option_json]
                }]
            })
            option_app_label_list.append(app_label_id)
            content_id_list.append({
                "id": app_label_id,
                'option': [content_type_id]
            })

    data = {
        'option_item_list': option_item_list,
        "select_list": context['widget']['value']
    }

    return json.dumps(data, cls=LazyEncoder)
