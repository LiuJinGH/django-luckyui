# Generated by Django 4.2.5 on 2025-01-23 15:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='luckyuser',
            name='last_login_datetime',
        ),
    ]
