# Generated by Django 2.2.5 on 2019-11-06 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sports', '0003_tournamentjoin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentjoin',
            name='phoneNumber',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]