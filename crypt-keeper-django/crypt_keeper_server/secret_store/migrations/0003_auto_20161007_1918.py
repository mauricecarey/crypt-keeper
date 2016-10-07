# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secret_store', '0002_auto_20161005_0709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privatekey',
            name='key',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='publickey',
            name='key',
            field=models.TextField(),
        ),
    ]
