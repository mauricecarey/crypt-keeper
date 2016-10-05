from django.contrib import admin
from .models import DocumentMetadata, DocumentDescription

# Register your models here.
admin.site.register(DocumentMetadata)
admin.site.register(DocumentDescription)
