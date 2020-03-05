from ....apraxiatorexception import ApraxiatorException


class SpeechDetectionException(ApraxiatorException):
    def get_message(self):
        return 'An Error Occurred Processing the Speech Sample'


class InvalidSpeechSampleException(ApraxiatorException):
    def __init__(self, issue, inner_error=None):
        super().__init__(inner_error)
        self.issue = issue

    def get_message(self):
        return 'Invalid Speech Sample: {}'.format(self.issue)

    def get_code(self):
        return 400
