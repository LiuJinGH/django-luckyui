from django.contrib import admin


class LuckyAdminSite(admin.AdminSite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__set_custom_login_form()

    def __set_custom_login_form(self):
        from luckyui.contrib.admin.captcha_forms import CaptchaAdminAuthenticationForm
        self.login_form = CaptchaAdminAuthenticationForm
