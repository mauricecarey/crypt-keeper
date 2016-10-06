
def decrypt(encrypted_symmetric_key, private_key):
    return 'decrypted(%s, %s)' % (encrypted_symmetric_key, private_key)


def encrypt(symmetric_key, public_key):
    return 'encrypted(%s, %s)' % (symmetric_key, public_key)


def sign_url(document_id):
    return 'signed_url_for(%s)' % document_id


def generate_symmetric_key():
    return 'this is a symmetric key'


def generate_document_id(document_metadata):
    return 'generated_document_id(%s)' % document_metadata.id
