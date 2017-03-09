from uuid import uuid4
from re import match
from boto3 import client
from botocore.client import Config
from botocore.exceptions import ClientError
from crypt_keeper_server.configuration import CONFIGURATION
from crypt_keeper_server.settings import LOG_LEVEL_DEFAULT
from logging import getLogger
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist

log = getLogger(__name__)
log.setLevel(CONFIGURATION.lookup('log:level', LOG_LEVEL_DEFAULT))

PUT = 'PUT'
GET = 'GET'
S3_URL_EXPIRATION_TIMEOUT = CONFIGURATION.lookup('s3:url_expiration_timeout', 600)
S3_BUCKET = CONFIGURATION.lookup('s3:bucket')

client_method_map = {
    GET: 'get_object',
    PUT: 'put_object',
}


def get_aws_client(client_type, config=None):
    if not config:
        config = Config(signature_version='s3v4')
    aws_access_key = CONFIGURATION.lookup('aws:access_key')
    aws_secret_key = CONFIGURATION.lookup('aws:secret_key')
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
        pass
    return group


def get_user_for_username(username):
    user = None
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        pass
    return user
