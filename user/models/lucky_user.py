from django.contrib.auth.models import AbstractUser
from luckyui.contrib.db import models as lucky_models


class LuckyUser(AbstractUser):
    class Meta:
        verbose_name = '系统用户'
        verbose_name_plural = '系统用户'

    phone = lucky_models.CharField(max_length=150, verbose_name="用户手机号")
    birthday = lucky_models.DateField(default=None, null=True, blank=True)

    nickname = lucky_models.CharField(verbose_name='昵称', max_length=50, help_text='在客户端显示的名字', null=True,
                                      blank=True, default='')

    def __str__(self):
        if self.nickname:
            return self.nickname
        else:
            return self.username

    def json(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'username': self.username,
            'phone': self.phone,
            'birthday': self.birthday.strftime('%Y-%m-%d') if self.birthday else None
        }
