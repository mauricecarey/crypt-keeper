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
from secret_store.helper import generate_new_key_pair


class Command(BaseCommand):
    help = 'Generates a new key pair.'

    def add_arguments(self, parser):
        parser.add_argument('key_size', type=int)
        parser.add_argument('-f', '--format', default='PEM')

    def handle(self, *args, **options):
        key_size = options.get('key_size', 2048)
        key_format = options.get('format', 'PEM')
        key_pair = generate_new_key_pair(key_size, key_format)
        self.stdout.write('Successfully generated key pair "%s"' % key_pair)
