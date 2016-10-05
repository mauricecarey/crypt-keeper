from django.contrib import admin
from .models import KeyPair, PublicKey, PrivateKey

# Register your models here.
admin.site.register(PrivateKey)
admin.site.register(PublicKey)
admin.site.register(KeyPair)
