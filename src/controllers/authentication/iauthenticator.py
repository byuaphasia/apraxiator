from flask import Request

class IAuthenticator:
    def get_user(self, r: Request):
        raise NotImplementedError()