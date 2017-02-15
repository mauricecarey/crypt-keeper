import json
from django.http.response import HttpResponseServerError
from django.contrib.auth.models import Group
from django.db import transaction
from tastypie.resources import Resource
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import MultiAuthentication, ApiKeyAuthentication
from tastypie.exceptions import ImmediateHttpResponse, Unauthorized
from tastypie.validation import Validation
from guardian.shortcuts import assign_perm
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


class UrlResource(Resource):
    document_id = fields.CharField(attribute='document_id')
    single_use_url = fields.CharField(attribute='single_use_url')
    symmetric_key = fields.CharField(attribute='symmetric_key')

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.document_id
        else:
            kwargs['pk'] = bundle_or_obj.document_id
        return kwargs


class DownloadUrlResource(UrlResource):
    document_metadata = fields.ToOneField(to=DocumentMetadataResource, attribute='document_metadata', full=True)

    class Meta:
        list_allowed_methods = []
        detail_allowed_methods = ['get']
        resource_name = '%s/download_url' % ROOT_RESOURCE_NAME
        object_class = Url
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def obj_get(self, bundle, **kwargs):
        document = DocumentDescription.objects.get(document_id=kwargs['pk'])
        user = bundle.request.user
        user_in_document_group = user.groups.filter(name=str(document.document_id)).exists()
        if not user_in_document_group or not user.has_perm('view_document_description', document):
            self.unauthorized_result(Unauthorized('{user} is not authorized.'.format(user=user.username)))
        symmetric_key = decrypt(document.encrypted_document_key, document.key_pair.private.key)
        single_use_url = sign_url(document.document_id, method=GET)
        download_url = Url(document.document_id, document.document_metadata, single_use_url, symmetric_key)
        return download_url


class UploadUrlResource(UrlResource):
    class Meta:
        allowed_methods = ['post']
        resource_name = '%s/upload_url' % ROOT_RESOURCE_NAME
        object_class = Url
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        excludes = ['document_metadata']
        validation = UploadValidation()

    def obj_create(self, bundle, **kwargs):
        if not super(UploadUrlResource, self).is_valid(bundle):
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

        default_key_pair = get_default_key_pair()
        if not default_key_pair:
            e = Exception('No default key pair defined.')
            e.response = HttpResponseServerError('Internal configuration error: No default key pair defined.')
            raise e
        symmetric_key = generate_symmetric_key()
        encrypted_symmetric_key = encrypt(symmetric_key, default_key_pair.public.key)
        current_user = bundle.request.user

        document_metadata_map = bundle.data.get('document_metadata', {})
        document = self.create_document(current_user, default_key_pair, document_metadata_map, encrypted_symmetric_key)

        single_use_url = sign_url(document.document_id, method=PUT)
        upload_url = Url(document_id=document.document_id, single_use_url=single_use_url, symmetric_key=symmetric_key)
        bundle.obj = upload_url
        return bundle

    @transaction.atomic()
    def create_document(self, current_user, default_key_pair, document_metadata_map, encrypted_symmetric_key):
        document_metadata = DocumentMetadata()
        document_metadata.compressed = document_metadata_map.get('compressed')
        document_metadata.content_length = document_metadata_map.get('content_length')
        document_metadata.content_type = document_metadata_map.get('content_type')
        document_metadata.name = document_metadata_map.get('name')
        document_metadata.uri = document_metadata_map.get('uri')
        document_metadata.save()

        document_id = generate_document_id(document_metadata)
        document = DocumentDescription()
        document.document_id = document_id
        document.document_metadata = document_metadata
        document.encrypted_document_key = encrypted_symmetric_key
        document.encrypted_document_size = 1337
        document.key_pair = default_key_pair
        document.customer = current_user
        document.save()

        document_group = Group()
        document_group.name = str(document_id)
        document_group.save()
        document_group.user_set.add(document.customer)

        assign_perm('view_document_description', document.customer, document)
        return document
