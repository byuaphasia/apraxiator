import unittest
import pytest
import json
import os

from .context import src
from src.controllers.authentication.jwtauthenticator import JWTAuthenticator, TokenExpiredException
from .testutils.requestutils import DummyRequest



import pathlib, os
_file_path = pathlib.Path(__file__).parent.absolute()

example_file = os.path.join(_file_path, '../apx-resources/auth/test_example.json')


@pytest.mark.skipif(not os.path.isfile(example_file), reason='APX resources directory must be available')
class TestJWTAuthenticator(unittest.TestCase):
    def setUp(self):
        example = json.load(open(example_file, 'r'))
        self.ex_jwt = example.get('token', '')
        self.ex_user = example.get('user', '')

    def test_getUser(self):
        r = DummyRequest().set_headers({'TOKEN': self.ex_jwt})
        auth = JWTAuthenticator()
        with self.assertRaises(TokenExpiredException):
            auth.get_user(r)

        username = auth.get_user(r, verify=False)
        self.assertEqual(self.ex_user, username)
