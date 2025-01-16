from captcha.fields import CaptchaField
from django.conf import settings
from django.contrib.admin.forms import AdminAuthenticationForm


class CaptchaAdminAuthenticationForm(AdminAuthenticationForm):
    # 增加验证码字段
    captcha = CaptchaField(error_messages={"invalid": "验证码错误", "required": "验证码必填", "incomplete": "请输入完整的验证码"})

    def clean(self):
        cleaned_data = super().clean()
        if settings.CAPTCHA_IGNORE_STR:
            captcha = self.data.get('captcha_1')
            if captcha == settings.CAPTCHA_IGNORE_STR:
                del self.errors['captcha']
        return cleaned_data
