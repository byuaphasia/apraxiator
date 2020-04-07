import json
import os
import logging


class Configuration:
    def __init__(self, name, dbName=None, s3Bucket=None, jwkFile=None, templatesDir=None, emailSender=None):
        logger = logging.getLogger(__name__)
        project_root = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../"))
        self.dbName = dbName
        self.s3Bucket = s3Bucket
        if jwkFile:
            self.jwkFile = os.path.realpath(os.path.join(project_root, jwkFile))
        else:
            self.jwkFile = None
        if templatesDir:
            self.templatesDir = os.path.realpath(os.path.join(project_root, templatesDir))
        else:
            self.templatesDir = None
        self.emailSender = emailSender
        logger.info('[event=config-loaded][configName=%s][config=%s]', name, self.to_json())

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def load_config(filename):
        current_dir = os.path.dirname(__file__)
        config = json.load(open(os.path.join(current_dir, filename), 'r'))
        return Configuration(**config)
