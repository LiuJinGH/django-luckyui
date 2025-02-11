# Generated by Django 4.2.5 on 2024-12-23 10:02

from django.db import migrations
import luckyui.contrib.db.models.fields.date_field
import luckyui.contrib.db.models.fields.date_time_field
import luckyui.contrib.db.models.fields.image_field


class Migration(migrations.Migration):

    dependencies = [
        ('test_demo', '0003_testmodelfields_date_field_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodelfields',
            name='image_field',
            field=luckyui.contrib.db.models.fields.image_field.ImageField(blank=True, default=None, help_text='嘎嘞', null=True, upload_to='test_demo/%Y/%m/%d/', verbose_name='image field'),
        ),
        migrations.AlterField(
            model_name='testmodelfields',
            name='date_field',
            field=luckyui.contrib.db.models.fields.date_field.DateField(default=None, help_text='嘎嘞', verbose_name='date field'),
        ),
        migrations.AlterField(
            model_name='testmodelfields',
            name='date_time_field',
            field=luckyui.contrib.db.models.fields.date_time_field.DateTimeField(default=None, help_text='嘎嘞', verbose_name='date time field'),
        ),
    ]
