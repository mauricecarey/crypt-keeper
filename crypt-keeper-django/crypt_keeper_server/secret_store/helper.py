from base64 import b64encode, b64decode
from re import match
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from .models import KeyPair, PrivateKey, PublicKey
from django.conf import settings
from logging import getLogger

log = getLogger(__name__)
log.setLevel(settings.LOG_LEVEL)

SEED_LENGTH = settings.CONFIGURATION.lookup('symmetric_key:seed_length', 128)
SYMMETRIC_KEY_LENGTH = settings.CONFIGURATION.lookup('symmetric_key:length', 32)
AES_CBC = 'AES|CBC'


def encode_key(key_bytes):
    return b64encode(key_bytes).decode('utf-8', 'backslashreplace')


def decode_key(key_text):
    return b64decode(key_text.encode('utf-8'))


def generate_new_key_pair(key_size, key_format):
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
    return key_pair


def get_default_key_pair():
    if KeyPair.objects.count() == 0:
        return None
    return KeyPair.objects.latest(field_name='created_on')


def decrypt(encrypted_symmetric_key, private_key):
    decoded_encrypted_symmetric_key = decode_key(encrypted_symmetric_key)
    decoded_private_key = private_key
    if not match(r'-+BEGIN RSA PRIVATE KEY-+', private_key):
        decoded_private_key = decode_key(private_key)
    key = RSA.importKey(decoded_private_key)
    cipher = PKCS1_OAEP.new(key)
    symmetric_key = cipher.decrypt(decoded_encrypted_symmetric_key)
    return encode_key(symmetric_key)


def encrypt(symmetric_key, public_key):
    decoded_symmetric_key = decode_key(symmetric_key)
    decoded_public_key = public_key
    if not match(r'-+BEGIN PUBLIC KEY-+', public_key):
        decoded_public_key = decode_key(public_key)
    key = RSA.importKey(decoded_public_key)
    cipher = PKCS1_OAEP.new(key)
    encrypted_symmetric_key = cipher.encrypt(decoded_symmetric_key)
    return encode_key(encrypted_symmetric_key)


def generate_symmetric_key(key_size=SYMMETRIC_KEY_LENGTH):
    seed = '1337:Crypt-Keeper:'.encode('utf-8') + Random.new().read(SEED_LENGTH)
    symmetric_key = SHA256.new(seed).digest()[:key_size]
    return encode_key(symmetric_key)
