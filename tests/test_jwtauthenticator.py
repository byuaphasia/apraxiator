import unittest
import json
import os

from .context import JWTAuthenticator, TokenExpiredException

example = json.load(open('../apx-resources/auth/test_example.json', 'r'))
ex_jwt = example.get('token', '')
ex_user = example.get('user', '')

class TestJWTAuthenticator(unittest.TestCase):
    def test_getUser(self):
        auth = JWTAuthenticator()
        with self.assertRaises(TokenExpiredException):
            auth.get_user(ex_jwt)

        username = auth.get_user(ex_jwt, verify=False)
        self.assertEqual(ex_user, username)