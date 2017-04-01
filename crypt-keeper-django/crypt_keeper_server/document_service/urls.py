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

from django.conf.urls import include, url
from . import views

from tastypie.api import Api
from secret_store.api import KeyPairResource, PublicKeyResource, PrivateKeyResource
from document_description_store.api import DocumentDescriptionResource, DocumentMetadataResource
from .api import DownloadUrlResource, UploadUrlResource, ShareResource

v1_api = Api(api_name='v1')
v1_api.register(KeyPairResource())
v1_api.register(PublicKeyResource())
v1_api.register(PrivateKeyResource())
v1_api.register(DocumentDescriptionResource())
v1_api.register(DocumentMetadataResource())
v1_api.register(DownloadUrlResource())
v1_api.register(UploadUrlResource())
v1_api.register(ShareResource())

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='homepage'),
    url(r'^my/$', views.MyView.as_view(), name='myview'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.DocumentDetailView.as_view(), name='detail'),
    url(r'^share/$', views.ShareView.as_view(), name='share'),
    url(r'^api/', include(v1_api.urls)),
]
