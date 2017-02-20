from django.contrib.auth.models import User, Group
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from guardian.shortcuts import assign_perm

from secret_store.helper import decrypt, AES_CBC
from document_description_store.models import DocumentDescription

BASE_DOWNLOAD_URL = '/api/v1/document_service/download_url/'
BASE_UPLOAD_URL = '/api/v1/document_service/upload_url/'


class DocumentServiceApiTestCase(ResourceTestCaseMixin, TestCase):
    fixtures = ['full_db_test_entries.json']

    def setUp(self):
        super(DocumentServiceApiTestCase, self).setUp()

        # Create a user
        self.username = 'tester'
        self.password = 'pass'
        self.user = User.objects.get(username=self.username)

        self.document = DocumentDescription.objects.get(customer=self.user)
        # add group for user
        document_group = Group()
        document_group.name = str(self.document.document_id)
        document_group.save()
        document_group.user_set.add(self.user)
        # add permissions for authorized user.
        auth_user = User.objects.get(username='authorized_other')
        document_group.user_set.add(auth_user)
        assign_perm('view_document_description', auth_user, self.document)
        self.assertTrue(auth_user.has_perm('view_document_description', self.document))

        self.download_url = '{base_url}{document_id}/'.format(
            base_url=BASE_DOWNLOAD_URL,
            document_id=self.document.document_id,
        )
        self.upload_url = '{base_url}'.format(base_url=BASE_UPLOAD_URL)

        self.api_key = 'test'

        self.document_metadata = {
            'content_type': self.document.document_metadata.content_type,
            'compressed': self.document.document_metadata.compressed,
            'content_length': str(self.document.document_metadata.content_length),
            'name': self.document.document_metadata.name,
            'uri': self.document.document_metadata.uri,
            'encryption_type': AES_CBC,
        }

    def get_credentials(self):
        return self.create_apikey(self.username, self.api_key)

    def test_download_get_list_unauthenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(BASE_DOWNLOAD_URL))

    def test_download_get_list_authenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(BASE_DOWNLOAD_URL, authentication=self.get_credentials()))

    def test_download_get_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.download_url))

    def check_download_response(self, response):
        response_map = self.deserialize(response)
        self.assertKeys(
            response_map,
            ['document_id', 'document_metadata', 'resource_uri', 'single_use_url', 'symmetric_key']
        )
        single_use_url = response_map.pop('single_use_url', None)
        self.assertIsNotNone(single_use_url)
        self.assertRegex(
            single_use_url,
            r'^https://s3.amazonaws.com/.*-crypt-keeper/{document_id}.*$'.format(document_id=self.document.document_id),
        )
        self.assertDictEqual(
            response_map,
            {
                'document_id': str(self.document.document_id),
                'resource_uri': self.download_url,
                'document_metadata': self.document_metadata,
                'symmetric_key': decrypt(self.document.encrypted_document_key, self.document.key_pair.private.key),
            }
        )

    def test_download_get_detail_json(self):
        response = self.api_client.get(self.download_url, authentication=self.get_credentials())
        self.assertValidJSONResponse(response)
        self.check_download_response(response)

    def test_download_get_detail_json_wrong_user(self):
        self.assertHttpUnauthorized(
            self.api_client.get(self.download_url, authentication=self.create_apikey('tester2', self.api_key))
        )

    def test_download_get_detail_json_authorized_user(self):
        response = self.api_client.get(
            self.download_url,
            authentication=self.create_apikey('authorized_other', self.api_key)
        )
        self.assertValidJSONResponse(response)
        self.check_download_response(response)

    def test_download_get_detail_xml(self):
        response = self.api_client.get(self.download_url, format='xml', authentication=self.get_credentials())
        self.assertValidXMLResponse(response)

    def test_upload_get_list_unauthenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(BASE_UPLOAD_URL))

    def test_upload_get_list_authenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(BASE_UPLOAD_URL, authentication=self.get_credentials()))

    def test_upload_get_detail_unauthenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(self.upload_url))

    def test_upload_get_detail_authenticated(self):
        self.assertHttpMethodNotAllowed(self.api_client.get(self.upload_url, authentication=self.get_credentials()))

    def test_upload_post_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.post(self.upload_url))

    def test_upload_post_detail_json_null_data(self):
        response = self.api_client.post(self.upload_url, authentication=self.get_credentials())
        self.assertHttpBadRequest(response)

    def test_upload_post_detail_json_empty_data(self):
        upload_data = {
            'document_metadata': {}
        }
        response = self.api_client.post(self.upload_url, data=upload_data, authentication=self.get_credentials())
        self.assertHttpBadRequest(response)

    def test_upload_post_detail_json_empty_name(self):
        self.document_metadata.pop('name', None)
        upload_data = {
            'document_metadata': self.document_metadata
        }
        response = self.api_client.post(self.upload_url, data=upload_data, authentication=self.get_credentials())
        self.assertHttpBadRequest(response)

    def test_upload_post_detail_json_empty_compressed(self):
        self.document_metadata.pop('compressed', None)
        upload_data = {
            'document_metadata': self.document_metadata
        }
        response = self.api_client.post(self.upload_url, data=upload_data, authentication=self.get_credentials())
        self.assertHttpBadRequest(response)

    def test_upload_post_detail_json_empty_content_length(self):
        self.document_metadata.pop('content_length', None)
        upload_data = {
            'document_metadata': self.document_metadata
        }
        response = self.api_client.post(self.upload_url, data=upload_data, authentication=self.get_credentials())
        self.assertHttpBadRequest(response)

    def test_upload_post_detail_json_empty_content_type(self):
        self.document_metadata.pop('content_type', None)
        upload_data = {
            'document_metadata': self.document_metadata
        }
        response = self.api_client.post(self.upload_url, data=upload_data, authentication=self.get_credentials())
        self.assertHttpBadRequest(response)

    def test_upload_post_detail_json_empty_uri(self):
        self.document_metadata.pop('uri', None)
        upload_data = {
            'document_metadata': self.document_metadata
        }
        response = self.api_client.post(self.upload_url, data=upload_data, authentication=self.get_credentials())
        self.assertHttpBadRequest(response)

    def test_upload_post_detail_json(self):
        self.assertEqual(DocumentDescription.objects.count(), 1)
        upload_data = {
            'document_metadata': self.document_metadata
        }
        response = self.api_client.post(self.upload_url, data=upload_data, authentication=self.get_credentials())
        self.assertHttpCreated(response)
        content = response.content.decode(response.charset)
        self.assertValidJSON(content)
        self.assertEqual(DocumentDescription.objects.count(), 2)
