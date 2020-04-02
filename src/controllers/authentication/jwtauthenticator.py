import jwt
import logging
from jwcrypto import jwk
from flask import Request

from .iauthenticator import IAuthenticator
from .unauthenticatedexceptions import TokenExpiredException, InvalidTokenException, UnauthenticatedException, MissingTokenException


class JWTAuthenticator(IAuthenticator):
    def __init__(self, jwk_file):
        keys_json = open(jwk_file, 'r').read()
        self.key_set = jwk.JWKSet().from_json(keys_json)
        self.logger = logging.getLogger(__name__)
        self.header_key = 'TOKEN'

    def get_user(self, r: Request, verify=True):
        token = self.get_token(r.headers)
        try:
            header = jwt.get_unverified_header(token)
            secret = self.key_set.get_key(header['kid']).export_to_pem()
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

    def get_token(self, http_headers):
        try:
            token = http_headers[self.header_key]
            return token
        except Exception as e:
            raise MissingTokenException(e)
