from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import DocumentMetadata, DocumentDescription


class DocumentDescriptionAdmin(GuardedModelAdmin):
    list_display = ('id', 'document_metadata', 'document_id', 'customer')
    search_fields = ('document_id', 'customer')
    ordering = ('id',)


class DocumentMetadataAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'content_length', 'content_type')
    search_fields = ('id', 'name')
    ordering = ('id',)

# Register your models here.
admin.site.register(DocumentMetadata, DocumentMetadataAdmin)
admin.site.register(DocumentDescription, DocumentDescriptionAdmin)
