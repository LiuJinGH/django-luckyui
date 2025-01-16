# Generated by Django 4.2.5 on 2024-12-25 08:55

from django.db import migrations, models
import django.db.models.deletion
import luckyui.contrib.db.models.fields.char_field


class Migration(migrations.Migration):

    dependencies = [
        ('test_demo', '0004_testmodelfields_image_field_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestSPU',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', luckyui.contrib.db.models.fields.char_field.CharField(max_length=150, verbose_name='名称')),
            ],
            options={
                'verbose_name': '商品',
                'verbose_name_plural': '商品管理',
            },
        ),
        migrations.CreateModel(
            name='TestSKU',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', luckyui.contrib.db.models.fields.char_field.CharField(max_length=50, verbose_name='规格名称')),
                ('spu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='test_demo.testspu', verbose_name='商品')),
            ],
            options={
                'verbose_name': '商品规格',
                'verbose_name_plural': '规格管理',
            },
        ),
    ]
