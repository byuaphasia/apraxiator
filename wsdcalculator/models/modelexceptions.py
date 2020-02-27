from ..apraxiatorexception import ApraxiatorException

class DataExportException(ApraxiatorException):
    def __init__(self, message, inner_error=None):
        super().__init__(inner_error)
        self.message = message

    def get_message(self):
        return f'Error on data export: {self.message}'