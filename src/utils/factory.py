import os

from src.storage.memorystorage import MemoryStorage
from src.storage.sqlstorage import SQLStorage
from src.filestorage.localfilestorage import LocalFileStorage
from src.filestorage.s3filestorage import S3FileStorage
from src.services.evaluation.evaluationservice import EvaluationService
from src.services.dataexport.dataexportservice import DataExportService
from src.services.waiver.waiverservice import WaiverService
from src.controllers.authentication.localauthenticator import LocalAuthenticator
from src.controllers.authentication.jwtauthenticator import JWTAuthenticator
from src.controllers.evaluationcontroller import EvaluationController
from src.controllers.dataexportcontroller import DataExportController
from src.controllers.waivercontroller import WaiverController
from src.utils.sender import LogSender, EmailSender
from src.utils.pdfgenerator import PDFGenerator, PDFLogger


class Factory:
    def __init__(self, storage, file_store, auth, sender, pdf_generator):
        self.storage = storage
        self.file_store = file_store
        self.auth = auth
        self.sender = sender
        self.pdf_generator = pdf_generator

        self.ev_service = EvaluationService(self.storage, self.file_store, self.sender, self.pdf_generator)
        self.de_service = DataExportService(self.storage, self.file_store)
        self.wv_service = WaiverService(self.storage, self.file_store, self.sender, self.pdf_generator)

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
    def create_limited_factory(storage_type='isolated'):
        auth = LocalAuthenticator()
        sender = LogSender()
        pdf_generator = PDFLogger()
        if storage_type == 'isolated':
            storage = MemoryStorage()
            file_store = LocalFileStorage()
        else:
            storage = SQLStorage()
            file_store = S3FileStorage()

        return Factory(storage, file_store, auth, sender, pdf_generator)
