"""crypt_keeper_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from secret_store.api import KeyPairResource, PublicKeyResource, PrivateKeyResource
from document_description_store.api import DocumentDescriptionResource, DocumentMetadataResource
from document_service.api import DownloadUrlResource, UploadUrlResource
from document_service import views
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(KeyPairResource())
v1_api.register(PublicKeyResource())
v1_api.register(PrivateKeyResource())
v1_api.register(DocumentDescriptionResource())
v1_api.register(DocumentMetadataResource())
v1_api.register(DownloadUrlResource())
v1_api.register(UploadUrlResource())

urlpatterns = [
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^$', views.IndexView.as_view(), name='homepage'),
    url(r'^login/$|^accounts/login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^my/$', views.MyView.as_view(), name='myview'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.DocumentDetailView.as_view(), name='detail'),
    url(r'^share/$', views.ShareView.as_view(), name='share')
]
