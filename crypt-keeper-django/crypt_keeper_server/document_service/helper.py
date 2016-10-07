from uuid import uuid4
from Crypto import Random
from Crypto.Hash import SHA256


def decrypt(encrypted_symmetric_key, private_key):
    return 'decrypted(%s, %s)' % (encrypted_symmetric_key, private_key)


def encrypt(symmetric_key, public_key):
    return 'encrypted(%s, %s)' % (symmetric_key, public_key)


def sign_url(document_id):
    return 'signed_url_for(%s)' % document_id


def generate_symmetric_key(key_size=None):
    length = key_size
    if not length:
        length = 32
    seed = '1337:Crypt-Keeper:%s' % Random.new().read(128)
    return SHA256.new(seed.encode('utf-8')).hexdigest()[:length]


def generate_document_id(document_metadata):
    return uuid4()
