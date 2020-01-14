from .storageexceptions import StorageException

class DBException(StorageException):
    def get_message(self):
        return 'Problem Accessing Database'

class ConnectionException(DBException):
    def get_message(self):
        return 'Unable to Connect to Database'