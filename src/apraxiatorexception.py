class ApraxiatorException(Exception):
    def __init__(self, inner_error=None):
        self.inner_error = inner_error

    def get_message(self):
        return 'An Internal Error Occurred'

    def get_code(self):
        return 500

    def to_response(self):
        r = {
            'errorMessage': self.get_message()
        }
        return r


class NotImplementedException(ApraxiatorException):
    def get_message(self):
        return "Whoops, Can't Do That"


class InvalidRequestException(ApraxiatorException):
    def __init__(self, issue, inner_error=None):
        super().__init__(inner_error)
        self.issue = issue

    def get_message(self):
        return 'Invalid Request: {}'.format(self.issue)

    def get_code(self):
        return 400
