from django.core.management.base import BaseCommand, CommandError
from Crypto.PublicKey import RSA
from secret_store.models import KeyPair, PrivateKey, PublicKey
from secret_store.helper import encode_key


class Command(BaseCommand):
    help = 'Generates a new key pair.'

    def add_arguments(self, parser):
        parser.add_argument('key_size', type=int)
        parser.add_argument('-f', '--format', default='PEM')

    def handle(self, *args, **options):
        key_size = options.get('key_size', 2048)
        key_format = options.get('format', 'PEM')
        key = RSA.generate(key_size)
        private = PrivateKey()
        private.key = encode_key(key.exportKey(format=key_format))
        private.save()
        public = PublicKey()
        public.key = encode_key(key.publickey().exportKey(format=key_format))
        public.save()
        key_pair = KeyPair()
        key_pair.private = private
        key_pair.public = public
        key_pair.save()
        self.stdout.write('Successfully generated key pair "%s"' % key_pair)
