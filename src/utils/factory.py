import os
import sys

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
from src.config.config import Configuration


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
        if len(sys.argv) > 1:
            config = Configuration.load_config(f'{sys.argv[1]}.json')
        else:
            env = os.environ.get('APX_ENV', 'local')
            config = Configuration.load_config(f'{env}.json')
        return Factory.process_config(config)

    @staticmethod
    def process_config(config: Configuration):
        if config.dbName:
            storage = SQLStorage(config.dbName)
        else:
            storage = MemoryStorage()

        if config.s3Bucket:
            file_store = S3FileStorage(config.s3Bucket)
        else:
            file_store = LocalFileStorage()

        if config.jwkFile:
            auth = JWTAuthenticator(config.jwkFile)
        else:
            auth = LocalAuthenticator()

        if config.templatesDir:
            pdf_generator = PDFGenerator(config.templatesDir)
        else:
            pdf_generator = PDFLogger()

        if config.emailSender:
            sender = EmailSender(config.emailSender)
        else:
            sender = LogSender()

        return Factory(storage, file_store, auth, sender, pdf_generator)

