class ApraxiatorException(Exception):
    def __init__(self, inner_error):
        self.inner_error = inner_error

    def get_message(self):
        return 'An Internal Error Occurred'

    def get_code(self):
        return 500

    def to_dict(self):
        r = {
            'errorMessage': self.get_message()
        }
        return r