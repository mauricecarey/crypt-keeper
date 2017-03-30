from uuid import uuid4
from re import match
from boto3 import client
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings
from logging import getLogger, WARN, INFO
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import assign_perm

from document_description_store.models import DocumentDescription

log = getLogger('crypt-keeper.' + __name__)

PUT = 'PUT'
GET = 'GET'
S3_URL_EXPIRATION_TIMEOUT = settings.CONFIGURATION.lookup('s3:url_expiration_timeout', 600)
S3_BUCKET = settings.CONFIGURATION.lookup('s3:bucket')

client_method_map = {
    GET: 'get_object',
    PUT: 'put_object',
}


def get_aws_client(client_type, config=None):
    if not config:
        config = Config(signature_version='s3v4')
    aws_access_key = settings.CONFIGURATION.lookup('aws:access_key')
    aws_secret_key = settings.CONFIGURATION.lookup('aws:secret_key')
    if aws_access_key and aws_secret_key:
        c = client(client_type, config=config, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    else:
        c = client(client_type, config=config)
    return c


def sign_url(document_id, method=GET):
    client_method = client_method_map.get(method, GET)
    s3 = get_aws_client('s3')
    params = {
        'Key': '%s' % document_id,
        'Bucket': S3_BUCKET,
    }
    url = s3.generate_presigned_url(ClientMethod=client_method,
                                    Params=params,
                                    ExpiresIn=S3_URL_EXPIRATION_TIMEOUT)
    return url


def check_bucket_exists(bucket_name):
    cl = get_aws_client('s3')
    try:
        response = cl.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        if match(r'^.*(404).*: Not Found$', '%s' % e):
            return False
        log.error('There was a ClientError: %s', e)
        raise e
    return response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200


def create_bucket(bucket_name):
    cl = get_aws_client('s3')
    try:
        response = cl.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        log.error('There was a ClientError: %s', e)
        raise e
    return response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200


def generate_document_id(document_metadata):
    return uuid4()


def get_group_for_document(document):
    group = None
    try:
        group = Group.objects.get(name=document.document_id)
    except ObjectDoesNotExist:
        if log.isEnabledFor(WARN):
            log.warning('Attempt to lookup non-existent group for document id {document_id}.'.format(
                document_id=document.document_id,
            ))
    return group


def get_user_for_username(username):
    user = None
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        if log.isEnabledFor(WARN):
            log.warning('Attempt to lookup non-existent user with name {username}.'.format(username=username))
    return user


def validate_username(username):
    if get_user_for_username(username) is not None:
        return True
    return False


def get_document_for_document_id(document_id):
    document = None
    try:
        document = DocumentDescription.objects.get(pk=document_id)
    except ObjectDoesNotExist:
        if log.isEnabledFor(WARN):
            log.warning('Attempt to lookup non-existent document with document id: {document_id}.'.format(
                document_id=document_id
            ))
    return document


def get_document_for_document_uuid(document_id):
    document = None
    try:
        document = DocumentDescription.objects.get(document_id=document_id)
    except ObjectDoesNotExist:
        if log.isEnabledFor(WARN):
            log.warning('Attempt to lookup non-existent document with document id: {document_id}.'.format(
                document_id=document_id
            ))
    return document


def validate_document_id(document_id):
    if get_document_for_document_id(document_id) is not None:
        return True
    return False


def validate_document_uuid(document_id):
    if get_document_for_document_uuid(document_id) is not None:
        return True
    return False


def add_permission_for_document(document, username):
    user = get_user_for_username(username)
    group = get_group_for_document(document)
    if group and user:
        group.user_set.add(user)
        group.save()
    assign_perm('view_document_description', user, document)
    if log.isEnabledFor(INFO):
        log.info('Adding permissions for {new_user} to access document id {document_id}.'.format(
            new_user=user,
            document_id=document.document_id,
        ))
