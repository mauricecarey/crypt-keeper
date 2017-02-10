from django.test import TestCase

from secret_store.helper import (
    get_default_key_pair,
    generate_new_key_pair,
    generate_symmetric_key,
    encrypt,
    decrypt,
)


class SecretStoreHelperTestCase(TestCase):
    fixtures = ['secret_store_helper_test_entries.json']

    def setUp(self):
        super(SecretStoreHelperTestCase, self).setUp()

    def test_get_default_key_pair_not_present(self):
        key_pair = get_default_key_pair()
        self.assertIsNone(key_pair)

    def test_generate_new_key_pair(self):
        key_pair = generate_new_key_pair(2048, 'PEM')
        self.assertIsNotNone(key_pair)
        key_id = key_pair.id
        key_pair = get_default_key_pair()
        self.assertIsNotNone(key_pair)
        self.assertEqual(key_pair.id, key_id)

    def test_symmetric_key_encrypt_decrypt_and_generation(self):
        key_pair = generate_new_key_pair(2048, 'PEM')
        self.assertIsNotNone(key_pair)
        public_key = key_pair.public.key
        self.assertIsNotNone(public_key)
        symmetric_key = generate_symmetric_key()
        self.assertIsNotNone(symmetric_key)
        encrypted_symmetric_key = encrypt(symmetric_key, public_key)
        self.assertIsNotNone(encrypted_symmetric_key)
        private_key = key_pair.private.key
        self.assertIsNotNone(private_key)
        decrypted_symmetric_key = decrypt(encrypted_symmetric_key, private_key)
        self.assertIsNotNone(decrypted_symmetric_key)
        self.assertEqual(symmetric_key, decrypted_symmetric_key)
