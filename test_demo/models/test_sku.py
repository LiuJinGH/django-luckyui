from django.db import models
from luckyui.contrib.db import models as lucky_models


class TestSKU(models.Model):

    class Meta:
        verbose_name = "商品规格"
        verbose_name_plural = "规格管理"

    spu = models.ForeignKey("test_demo.TestSPU", on_delete=models.CASCADE, verbose_name="商品")
    name = lucky_models.CharField(max_length=50, verbose_name="规格名称")

    def __str__(self):
        return self.name
