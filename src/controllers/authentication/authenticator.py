import os
from flask import Request

from .basicauthenticator import LocalAuthenticator
from .jwtauthenticator import JWTAuthenticator

def authenticate_request(func):
    def authenticate(r: Request, **kwargs):
        user = authenticate.authenticator.get_user(r)
        func(r, user, **kwargs)
    env = os.environ.get('APX_ENV')
    if env == 'local':
        authenticate.authenticator = LocalAuthenticator()
    else:
        authenticate.authenticator = JWTAuthenticator()
    return authenticate