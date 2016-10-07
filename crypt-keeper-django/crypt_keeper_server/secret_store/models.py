from django.db import models

# Create your models here.


class PublicKey(models.Model):
    key = models.TextField()

    def __str__(self):
        return 'public_key: %s' % self.key


class PrivateKey(models.Model):
    key = models.TextField()

    def __str__(self):
        return 'private_key: %s' % self.key


class KeyPair(models.Model):
    private = models.ForeignKey(PrivateKey)
    public = models.ForeignKey(PublicKey)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'ID: %s, %s, %s' % (self.pk, self.private, self.public)
