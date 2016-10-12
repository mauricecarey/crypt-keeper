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
