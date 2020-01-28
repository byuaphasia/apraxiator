import jwt
import json
import logging
from jwcrypto import jwk

from .unauthenticatedexceptions import TokenExpiredException, InvalidTokenException, UnauthenticatedException, MissingTokenException

HEADER_KEY = 'TOKEN'
auth_dir = '../apx-resources/auth/'

class JWTAuthenticator:
    def __init__(self):
        keys_json = open(auth_dir + 'jwk.json', 'r').read()
        self.keyset = jwk.JWKSet().from_json(keys_json)
        self.logger = logging.getLogger(__name__)
        self.header_key = 'TOKEN'

    def get_user(self, token, verify=True):
        try:
            header = jwt.get_unverified_header(token)
            secret = self.keyset.get_key(header['kid']).export_to_pem()
            payload = jwt.decode(token, key=secret, algorithms=header['alg'], verify=verify)
            username = payload['username']
            self.logger.info('[event=user-authenticated][user=%s][kid=%s]', username, header['kid'])
            return username
        except jwt.ExpiredSignatureError as e:
            self.logger.exception('JWT Token Expired')
            raise TokenExpiredException(e)
        except (jwt.DecodeError, jwt.InvalidTokenError) as e:
            self.logger.exception('Invalid JWT Token')
            raise InvalidTokenException(e)
        except Exception as e:
            self.logger.exception('Error Decoding JWT Token')
            raise UnauthenticatedException(e)

    @staticmethod
    def get_token(http_headers):
        try:
            token = http_headers[HEADER_KEY]
            return token
        except Exception as e:
            raise MissingTokenException(e)