import os

from src.storage import MemoryStorage, SQLStorage
from src.filestorage import LocalFileStorage, S3FileStorage
from src.services import EvaluationService, DataExportService, WaiverService
from src.controllers.authentication import LocalAuthenticator, JWTAuthenticator
from src.controllers import EvaluationController, DataExportController, WaiverController
from src.utils import LogSender, EmailSender, PDFGenerator


class Factory:
    def __init__(self, storage, file_store, auth, sender, pdf_generator):
        self.storage = storage
        self.file_store = file_store
        self.auth = auth
        self.sender = sender
        self.pdf_generator = pdf_generator

        self.ev_service = EvaluationService(self.storage, self.file_store, sender, pdf_generator)
        self.de_service = DataExportService(self.storage)
        self.wv_service = WaiverService(self.storage, self.sender, self.pdf_generator)

        self.ev_controller = EvaluationController(self.auth, self.ev_service)
        self.de_controller = DataExportController(self.auth, self.de_service)
        self.wv_controller = WaiverController(self.auth, self.wv_service)

    @staticmethod
    def create_factory():
        env = os.environ.get('APX_ENV', 'local')
        if env == 'local':
            file_store = LocalFileStorage()
            storage = MemoryStorage()
            auth = LocalAuthenticator()
            sender = LogSender()
        else:
            file_store = S3FileStorage()
            storage = SQLStorage()
            auth = JWTAuthenticator()
            sender = EmailSender()
        pdf_generator = PDFGenerator()

        return Factory(storage, file_store, auth, sender, pdf_generator)

    @staticmethod
    def create_isolated_factory(storage_type='mem'):
        file_store = LocalFileStorage()
        auth = LocalAuthenticator()
        sender = LogSender()
        if storage_type == 'db':
            storage = SQLStorage()
        else:
            storage = MemoryStorage()
        pdf_generator = PDFGenerator()

        return Factory(storage, file_store, auth, sender, pdf_generator)
