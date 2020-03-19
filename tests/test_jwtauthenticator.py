import unittest
import json

from .context import src
from src.controllers.authentication.jwtauthenticator import JWTAuthenticator, TokenExpiredException
from .utils.requestutils import DummyRequest

example = json.load(open('../apx-resources/auth/test_example.json', 'r'))
ex_jwt = example.get('token', '')
ex_user = example.get('user', '')


class TestJWTAuthenticator(unittest.TestCase):
    def test_getUser(self):
        r = DummyRequest().set_headers({'TOKEN': ex_jwt})
        auth = JWTAuthenticator()
        with self.assertRaises(TokenExpiredException):
            auth.get_user(r)

        username = auth.get_user(r, verify=False)
        self.assertEqual(ex_user, username)
