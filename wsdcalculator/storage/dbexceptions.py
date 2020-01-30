from .storageexceptions import StorageException

class DBException(StorageException):
    def get_message(self):
        return 'Problem Accessing Database'

class ConnectionException(DBException):
    def get_message(self):
        return 'Unable to Connect to Database'

class ResourceAccessException(DBException):
    def __init__(self, resource_id, inner_error=None):
        super().__init__(inner_error)
        self.resource_id = resource_id
    def get_message(self):
        return 'Problem Accessing Resource {} in Database'.format(self.resource_id)