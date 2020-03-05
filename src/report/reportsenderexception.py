from ..apraxiatorexception import ApraxiatorException


class ReportSenderException(ApraxiatorException):
    def get_message(self):
        return "Error sending report via email"
