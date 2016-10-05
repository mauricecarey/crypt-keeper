# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('secret_store', '0002_auto_20161005_0709'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentDescription',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('document_id', models.UUIDField(editable=False, default=uuid.uuid4)),
                ('encrypted_document_key', models.TextField()),
                ('encrypted_document_size', models.BigIntegerField()),
                ('customer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentMetadata',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.TextField()),
                ('content_length', models.BigIntegerField()),
                ('content_type', models.CharField(max_length=1000)),
                ('uri', models.URLField()),
                ('compressed', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='documentdescription',
            name='document_metadata',
            field=models.ForeignKey(to='document_description_store.DocumentMetadata'),
        ),
        migrations.AddField(
            model_name='documentdescription',
            name='key_pair',
            field=models.ForeignKey(to='secret_store.KeyPair'),
        ),
    ]
