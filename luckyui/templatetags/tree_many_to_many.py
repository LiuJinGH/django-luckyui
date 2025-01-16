import json
from django import template
from simpleui.templatetags.simpletags import LazyEncoder

register = template.Library()

# category_name表示模型的分类名  father_name表示分类的父节点
MODEL_CONFIG = [
    {'app_label': 'doctor', 'model_name': 'DoctorTool',
     'category_name': 'kind', 'category_model_name': 'DoctorToolKind',
     'father_name': ''},
]

@register.simple_tag
def get_tree_data(model_field, initial_value=None):
    """
    todo 以后需要优化一下性能  比如category_model一次性全部load出  然后再处理  以及可以el-tree懒加载
    """
    config = next((config for config in MODEL_CONFIG if config['model_name'] == model_field), None)
    if not config:
        raise ValueError("没有该模型")

    category_name = config['category_name']
    category_model_name = config['category_model_name']
    father_name = config['father_name']
    app_label = config['app_label']
    from django.apps import apps
    model = apps.get_model(app_label=app_label, model_name=model_field)
    category_model = apps.get_model(app_label=app_label, model_name=category_model_name)

    models = model.objects.all()
    root_categories = category_model.objects.filter(**{f"{father_name}__isnull": True}) if father_name else category_model.objects.all()

    def build_tree(categories):
        tree_data = []
        for category in categories:
            children = category_model.objects.filter(**{f"{father_name}__id": category.pk}) if father_name else None
            kind_data = {
                'category_id': category.pk,
                'label': str(category),
                'children': build_tree(children) if father_name and children.exists() else []
            }
            tree_data.append(kind_data)
        return tree_data

    def add_model_to_tree(tree_data, models):
        for model in models:
            category = getattr(model, category_name, None)

            if not category:
                tree_data.append({
                    'id': model.pk,
                    'label': str(model),
                    'children': []
                })
                continue

            find_and_add_node(tree_data, category, model)

    def find_and_add_node(tree_data, category, model):
        for item in tree_data:
            if item.get('category_id') == category.pk:
                item['children'].append({
                    'id': model.pk,
                    'label': str(model),
                    'children': []
                })
                return
            if 'children' in item:
                find_and_add_node(item['children'], category, model)

    category_tree_data = build_tree(root_categories)
    add_model_to_tree(category_tree_data, models)

    if initial_value and isinstance(initial_value, list):

        def mark_selected(data):
            for item in data:
                if item.get('id') in initial_value:
                    item['checked'] = True
                if 'children' in item and item['children']:
                    mark_selected(item['children'])

        mark_selected(category_tree_data)

    return json.dumps(category_tree_data, cls=LazyEncoder)
