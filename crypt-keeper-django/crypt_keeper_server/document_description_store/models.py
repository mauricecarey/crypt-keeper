#   Copyright 2017 Maurice Carey
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

from django.db import models
from secret_store.models import KeyPair
from django.contrib.auth.models import User
from uuid import uuid4
from secret_store.helper import AES_CBC
# Create your models here.


class DocumentMetadata(models.Model):
    name = models.TextField()
    content_length = models.BigIntegerField()
    content_type = models.CharField(max_length=1000)
    compressed = models.BooleanField(default=False)
    encryption_type = models.CharField(max_length=20, default=AES_CBC)

    def __str__(self):
        return '(%s, %s)' % (self.pk, self.name)


class DocumentDescription(models.Model):
    document_id = models.UUIDField(default=uuid4, editable=False)
    customer = models.ForeignKey(User)
    encrypted_document_key = models.TextField()
    encrypted_document_size = models.BigIntegerField()
    document_metadata = models.ForeignKey(DocumentMetadata)
    key_pair = models.ForeignKey(KeyPair)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('view_document_description', 'View Document Description'),
        )

    def __str__(self):
        return 'DocumentDescription: (%s, %s, %s, %s)' % (self.pk, self.document_id, self.document_metadata.name,
                                                          self.key_pair_id)
