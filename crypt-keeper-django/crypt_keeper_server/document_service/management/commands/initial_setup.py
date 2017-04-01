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

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from secret_store.helper import generate_new_key_pair, get_default_key_pair
from document_service.helper import check_bucket_exists, create_bucket

PROJECT_NAME = settings.PROJECT_NAME
CONFIGURATION = settings.CONFIGURATION


class Command(BaseCommand):
    help = 'Generates all required setup for %s.' % PROJECT_NAME

    def add_arguments(self, parser):
        parser.add_argument('--key_size', type=int, default=2048, help='The size of the public key pair to use.')
        parser.add_argument('-f', '--format', default='PEM', help='The format to store the public key pair in.')
        parser.add_argument('-b', '--bucket_name', default='crypt-keeper',
                            help='The suffix to use as bucket name for your %s file storage.' % PROJECT_NAME)
        parser.add_argument('aws_access_key', help='The AWS access key to use with %s.' % PROJECT_NAME)
        parser.add_argument('--aws_secret_key', help='The AWS secret key to use with %s.' % PROJECT_NAME)

    def handle(self, *args, **options):
        # generate a key pair
        key_pair = get_default_key_pair()
        if not key_pair:
            key_size = options.get('key_size', 2048)
            key_format = options.get('format', 'PEM')
            key_pair = generate_new_key_pair(key_size, key_format)
            self.stdout.write('Successfully generated key pair "%s"' % key_pair)
        else:
            self.stdout.write('Successfully found key pair "%s"' % key_pair)
        # Configure access key.
        access_key = options.get('aws_access_key')
        CONFIGURATION.set('aws:access_key', access_key)
        secret_key = options.get('aws_secret_key')
        if secret_key:
            CONFIGURATION.set('aws:secret_key', secret_key)
        self.stdout.write('Successfully set aws access key "%s"' % access_key)
        # setup bucket name.
        bucket_name = '%s-%s' % (access_key.lower(), options.get('bucket_name', 'crypt-keeper'))
        if not check_bucket_exists(bucket_name):
            create_bucket(bucket_name)
        CONFIGURATION.set('s3:bucket', bucket_name)
        self.stdout.write('Successfully set bucket name "%s"' % bucket_name)
        # Setup log level.
        if not CONFIGURATION.lookup('log:level'):
            CONFIGURATION.set('log:level', 'ERROR')
        # write the configuration to disk.
        CONFIGURATION.write_config()
        self.stdout.write('Successfully wrote configuration to disk.')
