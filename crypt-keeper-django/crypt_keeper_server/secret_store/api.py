from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import MultiAuthentication, ApiKeyAuthentication
from .models import KeyPair, PublicKey, PrivateKey

ROOT_RESOURCE_NAME = 'secret_store'


class PublicKeyResource(ModelResource):
    class Meta:
        queryset = PublicKey.objects.all()
        resource_name = '%s/public_key' % ROOT_RESOURCE_NAME
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()


class PrivateKeyResource(ModelResource):
    class Meta:
        queryset = PrivateKey.objects.all()
        resource_name = '%s/private_key' % ROOT_RESOURCE_NAME
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()


class KeyPairResource(ModelResource):
    private = fields.ToOneField(PrivateKeyResource, 'private', full=True)
    public = fields.ToOneField(PublicKeyResource, 'public', full=True)

    class Meta:
        queryset = KeyPair.objects.all()
        resource_name = '%s/key_pair' % ROOT_RESOURCE_NAME
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
