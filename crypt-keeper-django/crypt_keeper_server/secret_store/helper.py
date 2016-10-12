from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from .models import KeyPair, PrivateKey, PublicKey


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
