# Generated by Django 2.2.4 on 2019-11-18 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coda', '0002_auto_20190820_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='amouser',
            name='acc_age',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='amouser',
            name='acc_chat_activity',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='amouser',
            name='acc_friends_quantity',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='amouser',
            name='acc_wall_raws',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]