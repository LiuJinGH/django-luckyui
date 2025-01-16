from django.db import models
from django.utils.translation import gettext_lazy


class FieldTypeChoice(models.IntegerChoices):
    Test_1 = 0, gettext_lazy("test 1")
    Test_2 = 1, gettext_lazy("test 2")
    Test_3 = 2, gettext_lazy("test 3")
