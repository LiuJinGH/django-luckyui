# Generated by Django 4.2.5 on 2025-01-03 08:34

from django.db import migrations
import luckyui.contrib.db.models.fields.money_field


class Migration(migrations.Migration):

    dependencies = [
        ('test_demo', '0006_testmodelfields_type_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodelfields',
            name='money_field',
            field=luckyui.contrib.db.models.fields.money_field.MoneyField(default=0, help_text='单位：¥', verbose_name='money field'),
        ),
    ]
