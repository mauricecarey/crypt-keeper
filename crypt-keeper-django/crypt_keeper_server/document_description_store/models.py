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
    uri = models.URLField()
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
