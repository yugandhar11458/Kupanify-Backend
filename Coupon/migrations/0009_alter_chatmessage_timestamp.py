# Generated by Django 5.0 on 2023-12-08 10:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Coupon', '0008_chatmessage_delete_chat_remove_userprofile_chatwith_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
