from django.core.management.base import BaseCommand, CommandError
from secret_store.helper import generate_new_key_pair, get_default_key_pair
from document_service.helper import check_bucket_exists, create_bucket
from crypt_keeper_server.configuration import CONFIGURATION
from crypt_keeper_server.settings import PROJECT_NAME


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
        # write the configuration to disk.
        CONFIGURATION.write_config()
        self.stdout.write('Successfully wrote configuration to disk.')
