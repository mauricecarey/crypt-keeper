# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_description_store', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documentdescription',
            old_name='keyId',
            new_name='key_id',
        ),
    ]
