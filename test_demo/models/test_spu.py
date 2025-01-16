from django.db import models
from luckyui.contrib.db import models as lucky_models

from ckeditor_uploader.fields import RichTextUploadingField


class TestSPU(models.Model):

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品管理"

    name = lucky_models.CharField(verbose_name='名称', max_length=150)

    detail = RichTextUploadingField(verbose_name="商品详情", max_length=10000, default="", blank=True,
                                    config_name='default')

    def __str__(self):
        return self.name
