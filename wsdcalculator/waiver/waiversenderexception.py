from ..apraxiatorexception import ApraxiatorException


class WaiverSenderException(ApraxiatorException):
    def get_message(self):
        return "Error sending waiver via email"
