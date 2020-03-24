from ...apraxiatorexception import ApraxiatorException


class UnauthenticatedException(ApraxiatorException):
    def __init__(self, inner_error=None):
        super().__init__(inner_error)

    def get_message(self):
        return 'User Not Authenticated'

    def get_code(self):
        return 401


class TokenExpiredException(UnauthenticatedException):
    def get_message(self):
        return 'JWT Token Expired'


class InvalidTokenException(UnauthenticatedException):
    def get_message(self):
        return 'Invalid JWT Token'


class MissingTokenException(UnauthenticatedException):
    def get_message(self):
        return 'JWT Token Missing'
