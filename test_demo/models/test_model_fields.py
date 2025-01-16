from django.db import models
from luckyui.contrib.db import models as lucky_models

from .field_type_choice import FieldTypeChoice


class TestModelFields(models.Model):
    class Meta:
        verbose_name = "DB组件"
        verbose_name_plural = "DB组件"

    char_field = lucky_models.CharField(verbose_name='字符', max_length=150)
    switch_field = lucky_models.BooleanField(verbose_name='开关', default=False)
    integer_field = lucky_models.IntegerField(verbose_name='整型数值', default=0)
    date_field = lucky_models.DateField(verbose_name='日期', default=None)
    date_time_field = lucky_models.DateTimeField(verbose_name='日期时间', default=None)
    image_field = lucky_models.ImageField(verbose_name='图片', upload_to='test_demo/%Y/%m/%d/',
                                          null=True, blank=True,
                                          default=None)
    type_choice = lucky_models.IntegerField(verbose_name='整型枚举', choices=FieldTypeChoice.choices,
                                            default=FieldTypeChoice.Test_1)
    money_field = lucky_models.MoneyField(verbose_name='金额', help_text='单位：¥，精度2位小数。', default=0)

    def __str__(self):
        return '测试数据Fields实例'
