from .iauthenticator import IAuthenticator


class LocalAuthenticator(IAuthenticator):
    def __init__(self):
        self.user = 'test'

    def get_user(self, r):
        return self.user
