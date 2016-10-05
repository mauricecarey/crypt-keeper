from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import MultiAuthentication, ApiKeyAuthentication
from .models import DocumentDescription, DocumentMetadata

ROOT_RESOURCE_NAME = 'document_description_store'


class DocumentMetadataResource(ModelResource):
    class Meta:
        queryset = DocumentMetadata.objects.all()
        resource_name = '%s/document_metadata' % ROOT_RESOURCE_NAME
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()


class DocumentDescriptionResource(ModelResource):
    document_metadata = fields.ToOneField(DocumentMetadataResource, 'document_metadata', full=True)

    class Meta:
        queryset = DocumentDescription.objects.all()
        resource_name = '%s/document_description' % ROOT_RESOURCE_NAME
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
