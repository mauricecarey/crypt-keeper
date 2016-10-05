# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('secret_store', '0002_auto_20161005_0709'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentDescription',
            fields=[
                ('document_id', models.AutoField(serialize=False, primary_key=True)),
                ('encrypted_document_key', models.TextField()),
                ('encrypted_document_size', models.BigIntegerField()),
                ('customer_id', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentMetadata',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
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
            name='keyId',
            field=models.ForeignKey(to='secret_store.KeyPair'),
        ),
    ]
