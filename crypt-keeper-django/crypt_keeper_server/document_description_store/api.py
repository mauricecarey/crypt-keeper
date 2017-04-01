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
