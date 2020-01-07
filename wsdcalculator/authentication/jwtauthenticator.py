import jwt
import os
import logging

from .exceptions.unauthenticated import *

class JWTAuthenticator:
    def __init__(self):
        self.secret = os.environ['APX_SECRET']
        self.alg = 'RS256'
        self.logger = logging.getLogger(__name__)

    def getUser(self, token):
        try:
            payload = jwt.decode(token, key=self.secret, algorithms=self.alg)
        except jwt.ExpiredSignatureError as e:
            self.logger.exception('JWT Token Expired')
            raise TokenExpiredException(e)
        except (jwt.DecodeError, jwt.InvalidTokenError) as e:
            self.logger.exception('Invalid JWT Token')
            raise InvalidTokenException(e)
        except Exception as e:
            self.logger.exception('Error Decoding JWT Token')
            raise UnauthenticatedException(e)

        return payload['sub']