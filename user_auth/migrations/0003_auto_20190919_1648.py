# Generated by Django 2.2.5 on 2019-09-19 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0002_auto_20190919_1549'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='phone_num',
        ),
    ]
