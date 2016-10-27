from django.contrib.auth.models import User
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin

from secret_store.models import KeyPair

BASE_URL = '/api/v1/secret_store'


class SecretStoreApiTestCase(ResourceTestCaseMixin, TestCase):
    fixtures = ['secret_store_test_entries.json']

    def setUp(self):
        super(SecretStoreApiTestCase, self).setUp()

        # Create a user
        self.username = 'tester'
        self.password = 'pass'
        self.user = User.objects.get(username=self.username)

        key_pair = KeyPair.objects.first()
        self.key_pair_url = '{0}/key_pair/{1}/'.format(BASE_URL, key_pair.pk)
        self.private_key_url = '{0}/private_key/{1}/'.format(BASE_URL, key_pair.private.pk)
        self.public_key_url = '{0}/public_key/{1}/'.format(BASE_URL, key_pair.public.pk)

        self.api_key = 'test'

    def get_credentials(self):
        return self.create_apikey(self.username, self.api_key)

    def test_get_key_pair_list_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(BASE_URL + '/key_pair/'))

    def test_get_key_pair_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.key_pair_url))

    def test_get_key_pair_detail_json(self):
        response = self.api_client.get(self.key_pair_url, authentication=self.get_credentials())
        self.assertValidJSONResponse(response)
        self.assertKeys(
            self.deserialize(response),
            ['created_on', 'id', 'private', 'public', 'resource_uri']
        )

    def test_get_key_pair_detail_xml(self):
        self.assertValidXMLResponse(
            self.api_client.get(self.key_pair_url, format='xml', authentication=self.get_credentials())
        )

    def test_get_private_key_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.private_key_url))

    def test_get_private_key_detail_json(self):
        response = self.api_client.get(self.private_key_url, authentication=self.get_credentials())
        self.assertValidJSONResponse(response)
        self.assertKeys(
            self.deserialize(response),
            ['id', 'key', 'resource_uri']
        )

    def test_get_private_key_detail_xml(self):
        self.assertValidXMLResponse(
            self.api_client.get(self.private_key_url, format='xml', authentication=self.get_credentials())
        )

    def test_get_public_key_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.public_key_url))

    def test_get_public_key_detail_json(self):
        response = self.api_client.get(self.public_key_url, authentication=self.get_credentials())
        self.assertValidJSONResponse(response)
        self.assertKeys(
            self.deserialize(response),
            ['id', 'key', 'resource_uri']
        )

    def test_get_public_key_detail_xml(self):
        self.assertValidXMLResponse(
            self.api_client.get(self.public_key_url, format='xml', authentication=self.get_credentials())
        )
