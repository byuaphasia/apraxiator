import unittest
import pytest
import json
import os

from .context import src
from src.controllers.authentication.jwtauthenticator import JWTAuthenticator, TokenExpiredException
from .testutils.requestutils import DummyRequest


auth_root = os.path.join(os.path.dirname(__file__), '../../apx-resources/auth')


@pytest.mark.skipif(not os.path.isdir(auth_root), reason='APX resources directory must be available')
class TestJWTAuthenticator(unittest.TestCase):
    def setUp(self):
        example = json.load(open(os.path.join(auth_root, 'test_example.json'), 'r'))
        self.ex_jwt = example.get('token', '')
        self.ex_user = example.get('user', '')

    def test_getUser(self):
        r = DummyRequest().set_headers({'TOKEN': self.ex_jwt})
        auth = JWTAuthenticator(os.path.join(auth_root, 'jwk.json'))
        with self.assertRaises(TokenExpiredException):
            auth.get_user(r)

        username = auth.get_user(r, verify=False)
        self.assertEqual(self.ex_user, username)
