# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secret_store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='privatekey',
            name='key',
            field=models.CharField(max_length=2000, default='test'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='publickey',
            name='key',
            field=models.CharField(max_length=2000, default='test'),
            preserve_default=False,
        ),
    ]
