from base64 import b64encode, b64decode


def encode_key(key_bytes):
    return b64encode(key_bytes).decode('utf-8', 'backslashreplace')


def decode_key(key_text):
    return b64decode(key_text.encode('utf-8'))
