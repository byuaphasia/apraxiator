class LocalAuthenticator:
    def get_user(self, token, verify=True):
        return 'test'

    @staticmethod
    def get_token(http_headers):
        return ''