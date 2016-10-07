from uuid import uuid4
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from secret_store.helper import encode_key, decode_key
from re import match


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


def sign_url(document_id):
    return 'signed_url_for(%s)' % document_id


def generate_symmetric_key(key_size=None):
    length = key_size
    if not length:
        length = 32
    seed = '1337:Crypt-Keeper:'.encode('utf-8') + Random.new().read(128)
    symmetric_key = SHA256.new(seed).digest()[:length]
    return encode_key(symmetric_key)


def generate_document_id(document_metadata):
    return uuid4()
