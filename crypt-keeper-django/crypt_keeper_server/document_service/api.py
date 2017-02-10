import json
from tastypie.resources import Resource
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import MultiAuthentication, ApiKeyAuthentication
from tastypie.exceptions import ImmediateHttpResponse, Unauthorized
from tastypie.validation import Validation
from document_description_store.models import DocumentDescription, DocumentMetadata
from document_description_store import api as document_api
from secret_store.helper import get_default_key_pair, decrypt, generate_symmetric_key, encrypt
from .helper import sign_url, generate_document_id, GET, PUT

ROOT_RESOURCE_NAME = 'document_service'


class DocumentMetadataResource(document_api.DocumentMetadataResource):
    class Meta:
        include_resource_uri = False
        excludes = ['id']


class Url(object):
    def __init__(self, document_id=None, document_metadata=None, single_use_url=None, symmetric_key=None):
        self.document_id = document_id
        self.document_metadata = document_metadata
        self.single_use_url = single_use_url
        self.symmetric_key = symmetric_key


class UploadValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'Must provide document metadata.'}
        document_metadata = bundle.data.get('document_metadata', None)
        if not document_metadata:
            return {'__all__': 'Must provide document metadata.'}

        errors = {}
        expected_fields = ['name', 'compressed', 'content_length', 'content_type', 'uri']
        for field in expected_fields:
            if document_metadata.get(field, None) is None:
                errors[field] = 'Document metadata must have field: {field}'.format(field=field)
        return errors


class DownloadUrlResource(Resource):
    document_id = fields.CharField(attribute='document_id')
    document_metadata = fields.ToOneField(to=DocumentMetadataResource, attribute='document_metadata', full=True)
    single_use_url = fields.CharField(attribute='single_use_url')
    symmetric_key = fields.CharField(attribute='symmetric_key')

    class Meta:
        list_allowed_methods = []
        detail_allowed_methods = ['get']
        resource_name = '%s/download_url' % ROOT_RESOURCE_NAME
        object_class = Url
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.document_id
        else:
            kwargs['pk'] = bundle_or_obj.document_id
        return kwargs

    def obj_get(self, bundle, **kwargs):
        document = DocumentDescription.objects.get(document_id=kwargs['pk'])
        user = bundle.request.user
        if not user.has_perm('view_document_description', document):
            self.unauthorized_result(Unauthorized('{user} is not authorized.'.format(user=user.username)))
        symmetric_key = decrypt(document.encrypted_document_key, document.key_pair.private.key)
        single_use_url = sign_url(document.document_id, method=GET)
        download_url = Url(document.document_id, document.document_metadata, single_use_url, symmetric_key)
        return download_url


class UploadUrlResource(Resource):
    document_id = fields.CharField(attribute='document_id')
    single_use_url = fields.CharField(attribute='single_use_url')
    symmetric_key = fields.CharField(attribute='symmetric_key')

    class Meta:
        allowed_methods = ['post']
        resource_name = '%s/upload_url' % ROOT_RESOURCE_NAME
        object_class = Url
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        excludes = ['document_metadata']
        validation = UploadValidation()

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.document_id
        else:
            kwargs['pk'] = bundle_or_obj.document_id
        return kwargs

    def obj_create(self, bundle, **kwargs):
        if not super(UploadUrlResource, self).is_valid(bundle):
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))
        document_metadata_map = bundle.data.get('document_metadata', {})
        document_metadata = DocumentMetadata()
        document_metadata.compressed = document_metadata_map.get('compressed')
        document_metadata.content_length = document_metadata_map.get('content_length')
        document_metadata.content_type = document_metadata_map.get('content_type')
        document_metadata.name = document_metadata_map.get('name')
        document_metadata.uri = document_metadata_map.get('uri')
        document_metadata.save()

        default_key_pair = get_default_key_pair()
        if not default_key_pair:
            raise Exception('No default key pair defined.')
        symmetric_key = generate_symmetric_key()
        encrypted_symmetric_key = encrypt(symmetric_key, default_key_pair.public.key)

        document_id = generate_document_id(document_metadata)
        document = DocumentDescription()
        document.document_id = document_id
        document.document_metadata = document_metadata
        document.encrypted_document_key = encrypted_symmetric_key
        document.encrypted_document_size = 1337
        document.key_pair = default_key_pair
        document.customer = bundle.request.user
        document.save()

        single_use_url = sign_url(document.document_id, method=PUT)
        upload_url = Url(document_id=document.document_id, single_use_url=single_use_url, symmetric_key=symmetric_key)
        bundle.obj = upload_url
        return bundle
