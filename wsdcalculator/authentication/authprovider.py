import os

from .basicauthenticator import LocalAuthenticator
from .jwtauthenticator import JWTAuthenticator

def get_auth():
    env = os.environ.get('APX_ENV', None)
    if env == 'local':
        return LocalAuthenticator()
    else:
        return JWTAuthenticator()