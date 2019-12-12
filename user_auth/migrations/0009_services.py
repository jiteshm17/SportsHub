# Generated by Django 2.2.5 on 2019-12-12 06:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_auth', '0008_merge_20191210_0547'),
    ]

    operations = [
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_type', models.CharField(choices=[('Get Tournaments', 'Get Tournaments'), ('Join Tournament', 'Join Tournament'), ('Products', 'Products'), ('Bidding', 'Bidding')], max_length=150)),
                ('token', models.CharField(max_length=150)),
                ('user_name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]