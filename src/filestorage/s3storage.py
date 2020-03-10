import boto3
from botocore.exceptions import ClientError
import os

from ..services.evaluation import IEvaluationFileStorage
from .exceptions import FileAccessException, S3ConnectionException


class S3Storage(IEvaluationFileStorage):
    def __init__(self):
        try:
            self.access_key = os.environ['APX_AWS_ACCESS']
            self.secret_key = os.environ['APX_AWS_SECRET']
        except KeyError as e:
            raise S3ConnectionException(e.args[0], e)

    def save_recording(self, attempt_id: str, recording):
        self.save_file(attempt_id, 'recordings/', recording)

    def save_file(self, file_id: str, subdir: str, contents):
        try:
            s3 = boto3.client('s3', aws_access_key_id=self.access_key, aws_secret_key=self.secret_key)
        except Exception as e:
            raise S3ConnectionException(inner_error=e)
        try:
            s3.upload_fileobj(contents, 'BUCKET', subdir + file_id)
        except ClientError as e:
            raise FileAccessException(file_id, e)
