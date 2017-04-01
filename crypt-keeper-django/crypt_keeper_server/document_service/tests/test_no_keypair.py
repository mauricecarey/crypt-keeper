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

from django.contrib.auth.models import User
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from guardian.shortcuts import assign_perm

from secret_store.helper import decrypt
from document_description_store.models import DocumentDescription

BASE_SERVICE_URL = '/api/v1/secure_document_service/'
BASE_DOWNLOAD_URL = '{base_service_url}download_url/'.format(base_service_url=BASE_SERVICE_URL)
BASE_UPLOAD_URL = '{base_service_url}upload_url/'.format(base_service_url=BASE_SERVICE_URL)
BASE_SHARE_URL = '{base_service_url}share/'.format(base_service_url=BASE_SERVICE_URL)


class NoKeyPairApiTestCase(ResourceTestCaseMixin, TestCase):
    fixtures = ['no_key_pair_test_entries.json']

    def setUp(self):
        super(NoKeyPairApiTestCase, self).setUp()

        # Create a user
        self.username = 'tester'
        self.password = 'pass'
        self.user = User.objects.get(username=self.username)

        self.upload_url = '{base_url}'.format(base_url=BASE_UPLOAD_URL)

        self.api_key = 'test'

        self.document_metadata = {
            'content_type': '',
            'compressed': False,
            'content_length': str(10),
            'name': 'test.test',
            'uri': '',
        }

    def get_credentials(self):
        return self.create_apikey(self.username, self.api_key)

    def test_upload_post(self):
        self.assertEqual(DocumentDescription.objects.count(), 0)
        upload_data = {
            'document_metadata': self.document_metadata
        }
        response = self.api_client.post(self.upload_url, data=upload_data, authentication=self.get_credentials())
        self.assertHttpApplicationError(response)
        self.assertEqual(DocumentDescription.objects.count(), 0)
