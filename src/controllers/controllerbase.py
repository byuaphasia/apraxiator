from flask import Request

from .authentication import IAuthenticator


class ControllerBase:
    def __init__(self, authenticator: IAuthenticator):
        self.authenticator = authenticator


def authenticate_request(func):
    def authenticate(self: ControllerBase, r: Request, **kwargs):
        user = self.authenticator.get_user(r)
        return func(self, r, user, **kwargs)
    return authenticate
