# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-20 18:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_description_store', '0002_auto_20170211_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentmetadata',
            name='encryption_type',
            field=models.CharField(default='AES|CBC', max_length=20),
        ),
    ]