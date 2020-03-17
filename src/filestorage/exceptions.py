from ..apraxiatorexception import ApraxiatorException


class FileAccessException(ApraxiatorException):
    def __init__(self, file_id: str, inner_error=None):
        super().__init__(inner_error)
        self.file_id = file_id

    def get_message(self):
        return f'Error accessing file {self.file_id}'


class FileNotFoundException(ApraxiatorException):
    def __init__(self, file_id: str, inner_error=None):
        super().__init__(inner_error)
        self.file_id = file_id

    def get_message(self):
        return f'File not found {self.file_id}'

    def get_code(self):
        return 404


class S3ConnectionException(ApraxiatorException):
    def __init__(self, key_name=None, inner_error=None):
        super().__init__(inner_error)
        self.key_name = key_name

    def get_message(self):
        if self.key_name is None:
            return 'Error connecting to s3'
        else:
            return f'{self.key_name} required to connect to s3'
