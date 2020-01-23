import unittest
import json
import os

from .context import JWTAuthenticator, TokenExpiredException

ex_jwt = os.environ.get('APX_EX_JWT', '')
ex_user = os.environ.get('APX_EX_USR', '')

class TestJWTAuthenticator(unittest.TestCase):
    def test_getUser(self):
        auth = JWTAuthenticator()
        with self.assertRaises(TokenExpiredException):
            auth.get_user(ex_jwt)

        username = auth.get_user(ex_jwt, verify=False)
        self.assertEqual(ex_user, username)