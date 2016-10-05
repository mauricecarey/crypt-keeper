# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_description_store', '0002_auto_20161005_1803'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documentdescription',
            old_name='customer_id',
            new_name='customer',
        ),
        migrations.RenameField(
            model_name='documentdescription',
            old_name='key_id',
            new_name='key_pair',
        ),
    ]
