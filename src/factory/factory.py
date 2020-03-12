import os

from ..storage import MemoryStorage, SQLStorage
from ..filestorage import LocalFileStorage, S3FileStorage
from ..services import EvaluationService, DataExportService
from ..controllers.authentication import LocalAuthenticator, JWTAuthenticator
from ..controllers import EvaluationController, DataExportController


class Factory:
    def __init__(self, storage, file_store, auth):
        self.storage = storage
        self.file_store = file_store
        self.auth = auth

        self.ev_service = EvaluationService(self.storage, self.file_store)
        self.de_service = DataExportService(self.storage)

        self.ev_controller = EvaluationController(self.auth, self.ev_service)
        self.de_controller = DataExportController(self.auth, self.de_service)

    @staticmethod
    def create_factory():
        env = os.environ.get('APX_ENV', 'local')
        if env == 'local':
            file_store = LocalFileStorage()
            storage = MemoryStorage()
            auth = LocalAuthenticator()
        else:
            file_store = S3FileStorage()
            storage = SQLStorage()
            auth = JWTAuthenticator()

        return Factory(storage, file_store, auth)

    @staticmethod
    def create_isolated_factory(storage_type='mem'):
        file_store = LocalFileStorage()
        auth = LocalAuthenticator()
        if storage_type == 'db':
            storage = SQLStorage()
        else:
            storage = MemoryStorage()

        return Factory(storage, file_store, auth)
