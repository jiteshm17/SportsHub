# Generated by Django 2.2.5 on 2019-09-21 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20190920_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='headline',
            name='site',
            field=models.TextField(default='asdf'),
        ),
        migrations.AddField(
            model_name='headline',
            name='time',
            field=models.TextField(default='wow'),
        ),
    ]
