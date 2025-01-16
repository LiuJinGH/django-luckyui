import html
import re
from django import template
from django.template.response import TemplateResponse
from simpleui.templatetags.simpletags import _import_reload

from .base import InclusionAdminNode
from django.template.context import Context
from simpleui.templatetags.simpletags import *

register = template.Library()


def detail_submit_row(context):
    """
    Display the row of buttons for delete and save.
    """
    add = context["add"]
    change = context["change"]
    is_popup = context["is_popup"]
    save_as = context["save_as"]
    show_save = context.get("show_save", True)
    show_save_and_add_another = context.get("show_save_and_add_another", True)
    show_save_and_continue = context.get("show_save_and_continue", True)
    has_add_permission = context["has_add_permission"]
    has_change_permission = context["has_change_permission"]
    has_view_permission = context["has_view_permission"]
    has_editable_inline_admin_formsets = context["has_editable_inline_admin_formsets"]
    can_save = (
            (has_change_permission and change)
            or (has_add_permission and add)
            or has_editable_inline_admin_formsets
    )
    can_save_and_add_another = (
            has_add_permission
            and not is_popup
            and (not save_as or add)
            and can_save
            and show_save_and_add_another
    )
    can_save_and_continue = (
            not is_popup and can_save and has_view_permission and show_save_and_continue
    )
    can_change = has_change_permission or has_editable_inline_admin_formsets
    ctx = Context(context)
    ctx.update(
        {
            "can_change": can_change,
            "show_delete_link": (
                    not is_popup
                    and context["has_delete_permission"]
                    and change
                    and context.get("show_delete", True)
            ),
            "show_save_as_new": not is_popup
                                and has_add_permission
                                and change
                                and save_as,
            "show_save_and_add_another": can_save_and_add_another,
            "show_save_and_continue": can_save_and_continue,
            "show_save": show_save and can_save,
            "show_close": not (show_save and can_save),
        }
    )
    return ctx


@register.tag(name="detail_submit_row")
def detail_submit_row_tag(parser, token):
    return InclusionAdminNode(
        parser, token, func=detail_submit_row, template_name="detail_submit_line.html"
    )


@register.simple_tag(takes_context=True)
def lucky_menus(context, _get_config=None):
    """
    菜单标签

    context: index.html
    """

    # 如果 有role_menu 直接拦截并返回
    role_menu = context.get('role_menu')
    if role_menu:
        print('存在 role_menu')
        shortcut_menu = []
        menu_str = ''

        # 每次刷新，更新快捷菜单的eid
        for item in shortcut_menu:
            if item['eid']:
                item['eid'] = item['eid'] + menu_str
            else:
                item['eid'] = menu_str

        item = {
            "name": "快捷菜单",
            "icon": "fa-solid fa-file-circle-minus",
            "eid": "shortcut_menu",
            "models": shortcut_menu
        }
        role_menu.insert(0, item)
        menus_string = json.dumps(role_menu, cls=LazyEncoder)
        # 把data放入session中，其他地方可以调用
        if not isinstance(context, dict) and context.request:
            context.request.session['_menus'] = menus_string
        return '<script type="text/javascript">var menus={}</script>'.format(menus_string)

    data = []

    # return request.user.has_perm("%s.%s" % (opts.app_label, codename))
    if not _get_config:
        _get_config = get_config

    config = _get_config('SIMPLEUI_CONFIG')
    if not config:
        config = {}

    if config.get('dynamic', False) is True:
        config = _import_reload(_get_config('DJANGO_SETTINGS_MODULE')).SIMPLEUI_CONFIG

    app_list = context.get('app_list')
    for app in app_list:
        # 获取APP 列表
        _models = []
        if app.get('models'):
            model_menu_list = []
            model_id_list = []
            for m in app.get('models'):
                # 获取APP下的模型列表

                model_dict = m.get('model')
                model_item = {
                    'name': m.get('name'),
                    'icon': get_icon(m.get('object_name'), unicode_to_str(m.get('name'))),
                    'url': m.get('admin_url'),
                    'addUrl': m.get('add_url'),
                    'breadcrumbs': [{
                        'name': app.get('name'),
                        'icon': get_icon(app.get('app_label'), app.get('name'))
                    }, {
                        'name': m.get('name'),
                        'icon': get_icon(m.get('object_name'), unicode_to_str(m.get('name')))
                    }]
                }

                if hasattr(model_dict, 'model_icon'):
                    model_item['icon'] = model_dict.model_icon

                if hasattr(model_dict, 'menu'):
                    model_menu = model_dict.menu

                    if model_menu['id'] in model_id_list:
                        # 已存在
                        menu_index = model_id_list.index(model_menu['id'])
                        model_menu_list[menu_index]['models'].append(model_item)
                    else:
                        # 不存在
                        model_menu_list.append({
                            'name': model_menu['name'],
                            'icon': model_menu['icon'],
                            'models': [model_item]
                        })
                        model_id_list.append(model_menu['id'])
                else:
                    _models.append(model_item)

            _models = _models + model_menu_list

        _views = []

        if app.get('views'):
            view_menu_list = app.get('views')
            _views = _views + view_menu_list

        if len(_models) > 0 or len(_views) > 0:
            module = {
                'name': app.get('name'),
                'icon': get_icon(app.get('app_label'), app.get('name')),
                'models': _models,
                'views': _views
            }
            data.append(module)

    # 如果有menu 就读取，没有就调用系统的
    key = 'system_keep'
    if config and 'menus' in config:
        if config.get(key, None):
            temp = config.get('menus')
            for i in temp:
                # 处理面包屑
                if 'models' in i:
                    for k in i.get('models'):
                        k['breadcrumbs'] = [{
                            'name': i.get('name'),
                            'icon': i.get('icon')
                        }, {
                            'name': k.get('name'),
                            'icon': k.get('icon')
                        }]
                else:
                    i['breadcrumbs'] = [{
                        'name': i.get('name'),
                        'icon': i.get('icon')
                    }]
                data.append(i)
        else:
            data = config.get('menus')

    # 获取侧边栏排序, 如果设置了就按照设置的内容排序, 留空则表示默认排序以及全部显示
    if config.get('menu_display') is not None:
        display_data = list()
        for _app in data:
            if _app['name'] not in config.get('menu_display'):
                continue
            _app['_weight'] = config.get('menu_display').index(_app['name'])
            display_data.append(_app)
        display_data.sort(key=lambda x: x['_weight'])
        data = display_data

    # 给每个菜单增加一个唯一标识，用于tab页判断
    eid = 1000
    handler_eid(data, eid)
    menus_string = json.dumps(data, cls=LazyEncoder)

    # 把data放入session中，其他地方可以调用
    if not isinstance(context, dict) and context.request:
        context.request.session['_menus'] = menus_string

    return '<script type="text/javascript">var menus={}</script>'.format(menus_string)


@register.simple_tag(takes_context=True)
def lucky_home(context):
    return TemplateResponse(
        context.request, "admin/home.html", context
    )


@register.simple_tag(takes_context=True)
def get_log_iframe_value(context):
    value = context['original'].response_status_content
    res = format_value(value)
    return res


@register.simple_tag(takes_context=True)
def get_iframe_content_value(context):
    value = context['original'].content
    res = format_value(value)
    return res


@register.simple_tag(takes_context=True)
def get_text(context):
    # 富文本转纯文本
    value = context['original'].content
    htmlContent = html.unescape(value)
    regex = r'\>.*?\<'
    listAll = re.findall(regex, htmlContent)
    listToSave = [i[1:-1] for i in listAll if i != '><' and len(i) > 2]
    strContent = ''.join(listToSave)
    return strContent


def format_value(value):
    value = re.sub(r"\n", "", value)
    if "b'<!DOCTYPE html>" in value:
        byte_string = eval(value)
        value = byte_string.decode('utf-8')
    else:
        try:
            value = json.loads(value)
        except Exception:
            pass
        else:
            value = json.dumps(value, ensure_ascii=False)
    return value


@register.filter
def get_lucky_filter(spec):
    if hasattr(spec, 'type'):
        return spec.type
    return ''
