class UnauthenticatedException(Exception):
    def __init__(self, inner_error=None):
        self.inner_error = inner_error
    
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