from django.contrib.admin.apps import AdminConfig


class LuckyAdminConfig(AdminConfig):
    # 必须是字符串的引入形式，不能直接给个类
    default_site = 'luckyui.contrib.admin_site.LuckyAdminSite'
