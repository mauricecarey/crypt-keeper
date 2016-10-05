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
from secret_store.api import KeyPairResource, PublicKeyResource, PrivateKeyResource
from document_description_store.api import DocumentDescriptionResource, DocumentMetadataResource
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(KeyPairResource())
v1_api.register(PublicKeyResource())
v1_api.register(PrivateKeyResource())
v1_api.register(DocumentDescriptionResource())
v1_api.register(DocumentMetadataResource())

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
]
