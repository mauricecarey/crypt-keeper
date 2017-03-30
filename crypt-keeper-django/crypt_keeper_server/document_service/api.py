from django.http.response import HttpResponseServerError
from django.contrib.auth.models import Group
from django.db import transaction
from tastypie.resources import Resource
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.exceptions import ImmediateHttpResponse, Unauthorized
from tastypie.validation import Validation
from guardian.shortcuts import assign_perm
from document_description_store.models import DocumentDescription, DocumentMetadata
from document_description_store import api as document_api
from secret_store.helper import get_default_key_pair, decrypt, generate_symmetric_key, encrypt, AES_CBC
from .helper import (
    sign_url,
    generate_document_id,
    GET,
    PUT,
    validate_username,
    validate_document_uuid,
    add_permission_for_document,
    get_document_for_document_uuid,
    get_group_for_document,
)
from django.conf import settings
from logging import getLogger, DEBUG
from uuid import UUID

log = getLogger('crypt-keeper.' + __name__)

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


class Share(object):
    def __init__(self, document_id=None, username=None, users=None):
        self.document_id = document_id
        self.username = username
        self.users = users


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


class ShareValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return 'Must provide document id and username.'
        document_id = bundle.data.get('document_id', None)
        document_validation = ShareValidation.document_id_validation(document_id, bundle.request.user)
        if document_validation is not None:
            return document_validation
        username = bundle.data.get('username', None)
        if username is None:
            return 'Must provide username.'
        if not validate_username(username):
            return 'Must provide a valid username.'

    @classmethod
    def document_id_validation(cls, document_id, user):
        if document_id is None:
            return 'Must provide document id.'
        try:
            document_uuid = UUID(document_id)
            if not validate_document_uuid(document_uuid):
                return 'Must provide a valid document id.'
        except ValueError as e:
            msg = 'Request with badly formed document ID string: {document_id}'.format(document_id=document_id)
            log.info(msg, exc_info=e)
            return msg
        return None


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
            log.warning('{user} attempted to access {document_id}'.format(
                user=user.username,
                document_id=document.document_id,
            ))
            self.unauthorized_result(Unauthorized('{user} is not authorized.'.format(user=user.username)))
        symmetric_key = decrypt(document.encrypted_document_key, document.key_pair.private.key)
        single_use_url = sign_url(document.document_id, method=GET)
        download_url = Url(document.document_id, document.document_metadata, single_use_url, symmetric_key)
        if log.isEnabledFor(DEBUG):
            log.debug('Generated download URL {download_url} for {user}.'.format(
                download_url=download_url,
                user=user.username,
            ))
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
        log.info('Received request to create a new document upload record.')

        default_key_pair = get_default_key_pair()
        if not default_key_pair:
            err = 'No default key pair defined.'
            e = Exception(err)
            e.response = HttpResponseServerError('Internal configuration error: {error}.'.format(error=err))
            log.critical(err)
            raise e
        symmetric_key = generate_symmetric_key()
        if log.isEnabledFor(DEBUG):
            log.debug('Generated symmetric key for request: {key}.'.format(
                key=symmetric_key
            ))
        encrypted_symmetric_key = encrypt(symmetric_key, default_key_pair.public.key)
        if log.isEnabledFor(DEBUG):
            log.debug('Encrypted symmetric key for request: {key}.'.format(
                key=encrypted_symmetric_key
            ))
        current_user = bundle.request.user
        if log.isEnabledFor(DEBUG):
            log.debug('User for request: {user}.'.format(
                user=current_user
            ))

        document_metadata_map = bundle.data.get('document_metadata', {})
        document = self.create_document(current_user, default_key_pair, document_metadata_map, encrypted_symmetric_key)
        log.info('Document created for request.')

        single_use_url = sign_url(document.document_id, method=PUT)
        if log.isEnabledFor(DEBUG):
            log.debug('Created single use URL for request: {url}.'.format(
                url=single_use_url
            ))

        upload_url = Url(document_id=document.document_id, single_use_url=single_use_url, symmetric_key=symmetric_key)
        if log.isEnabledFor(DEBUG):
            log.debug('Generated upload URL {upload_url} for {user}.'.format(
                upload_url=upload_url,
                user=current_user.username,
            ))
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
        document_metadata.encryption_type = document_metadata_map.get('encryption_type', AES_CBC)
        document_metadata.save()
        if log.isEnabledFor(DEBUG):
            log.debug('Created document metadata for request: {meta}.'.format(
                meta=document_metadata
            ))

        document_id = generate_document_id(document_metadata)
        document = DocumentDescription()
        document.document_id = document_id
        document.document_metadata = document_metadata
        document.encrypted_document_key = encrypted_symmetric_key
        document.encrypted_document_size = 1337
        document.key_pair = default_key_pair
        document.customer = current_user
        document.save()
        if log.isEnabledFor(DEBUG):
            log.debug('Created document for request: {document}.'.format(
                document=document
            ))

        document_group = Group()
        document_group.name = str(document_id)
        document_group.save()
        document_group.user_set.add(document.customer)
        if log.isEnabledFor(DEBUG):
            log.debug('Created document group for request: {group}.'.format(
                group=document_group
            ))

        assign_perm('view_document_description', document.customer, document)
        return document


class ShareResource(Resource):
    document_id = fields.CharField(attribute='document_id', null=True)
    username = fields.CharField(attribute='username', null=True)
    users = fields.ListField(attribute='users', null=True)

    class Meta:
        list_allowed_methods = ['post']
        detail_allowed_methods = ['get']
        resource_name = '%s/share' % ROOT_RESOURCE_NAME
        object_class = Share
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        validation = ShareValidation()

    def dehydrate(self, bundle):
        if bundle is None or bundle.data is None:
            return bundle
        data = dict(bundle.data)
        for key in data:
            if data.get(key) is None:
                del bundle.data[key]
        return bundle

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            if isinstance(bundle_or_obj.obj, Share):
                kwargs['pk'] = bundle_or_obj.obj.document_id
        elif isinstance(bundle_or_obj, Share):
            kwargs['pk'] = bundle_or_obj.document_id
        return kwargs

    def obj_create(self, bundle, **kwargs):
        if not super().is_valid(bundle):
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))
        log.info('Received request to share a document.')
        user = bundle.request.user
        if log.isEnabledFor(DEBUG):
            log.debug('User for request: {user}.'.format(
                user=user
            ))

        document_id = bundle.data.get('document_id')
        username = bundle.data.get('username')
        document = get_document_for_document_uuid(document_id)
        if document.customer != user:
            self.unauthorized_result(Unauthorized(
                '{user} is not authorized for operations on this document.'.format(user=user.username)
            ))

        add_permission_for_document(document, username)

        bundle.obj = Share(document_id, username)
        return bundle

    def obj_get(self, bundle, **kwargs):
        document_id = kwargs['pk']
        user = bundle.request.user
        validation_message = ShareValidation.document_id_validation(document_id, user)
        if validation_message is not None:
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, validation_message))
        document = DocumentDescription.objects.get(document_id=document_id)
        if document.customer != user:
            self.unauthorized_result(Unauthorized(
                '{user} is not authorized for operations on this document.'.format(user=user.username)
            ))
        document_group = get_group_for_document(document)
        users = [x.username for x in document_group.user_set.all()]
        return Share(users=users, document_id=document_id)
