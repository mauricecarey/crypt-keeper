#   Copyright 2017 Maurice Carey
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
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
