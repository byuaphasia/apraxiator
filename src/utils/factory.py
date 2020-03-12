import os

from ..storage import MemoryStorage, SQLStorage
from ..filestorage import LocalFileStorage, S3FileStorage
from ..services import EvaluationService, DataExportService, WaiverService
from ..controllers.authentication import LocalAuthenticator, JWTAuthenticator
from ..controllers import EvaluationController, DataExportController, WaiverController
from .sender import LogSender, EmailSender
from .pdfgenerator import PDFGenerator, PDFLogger


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
            pdf_generator = PDFLogger()
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
        pdf_generator = PDFLogger()
        if storage_type == 'db':
            storage = SQLStorage()
        else:
            storage = MemoryStorage()

        return Factory(storage, file_store, auth, sender, pdf_generator)
