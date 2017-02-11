# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('document_description_store', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documentdescription',
            options={'permissions': (('view_document_description', 'View Document Description'),)},
        ),
        migrations.AddField(
            model_name='documentdescription',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 2, 11, 16, 21, 31, 52123, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
