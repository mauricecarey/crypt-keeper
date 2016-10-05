from django.db import models
from secret_store.models import KeyPair
from django.contrib.auth.models import User
# Create your models here.


class DocumentMetadata(models.Model):
    name = models.TextField()
    content_length = models.BigIntegerField()
    content_type = models.CharField(max_length=1000)
    uri = models.URLField()
    compressed = models.BooleanField(default=False)

    def __str__(self):
        return 'DocumentMetadata: (%s, %s)' % (self.pk, self.name)


class DocumentDescription(models.Model):
    document_id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(User)
    encrypted_document_key = models.TextField()
    encrypted_document_size = models.BigIntegerField()
    document_metadata = models.ForeignKey(DocumentMetadata)
    keyId = models.ForeignKey(KeyPair)

    def __str__(self):
        return 'DocumentDescription: (%s, %s)' % (self.pk, self.document_metadata.name)
