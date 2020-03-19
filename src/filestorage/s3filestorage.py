import boto3
from botocore.exceptions import ClientError
import os

from src.services.waiver.iwaiverfilestorage import IWaiverFileStorage
from src.services.evaluation.ievaluationfilestorage import IEvaluationFileStorage
from src.services.dataexport.idataexportfilestorage import IDataExportFileStorage
from src.filestorage.exceptions import FileAccessException, FileNotFoundException, S3ConnectionException


class S3FileStorage(IEvaluationFileStorage, IDataExportFileStorage, IWaiverFileStorage):
    def __init__(self, bucket='appraxia'):
        try:
            self.access_key = os.environ['APX_AWS_ACCESS']
            self.secret_key = os.environ['APX_AWS_SECRET']
            self.s3 = boto3.client('s3', aws_access_key_id=self.access_key, aws_secret_key=self.secret_key)
            self.bucket = bucket
            self.recordings_dir = 'recordings/'
            self.waivers_dir = 'waivers/'
            self.tmp_dir = os.path.realpath(__file__ + '/../../tmp')
            if not os.path.isdir(self.tmp_dir):
                os.mkdir(self.tmp_dir)
        except KeyError as e:
            raise S3ConnectionException(e.args[0], e)
        except Exception as e:
            raise S3ConnectionException(e)

    ''' IEvaluationFileStorage methods '''

    def save_recording(self, attempt_id: str, recording):
        self.upload_file(attempt_id, self.recordings_dir, recording)

    ''' IDataExportFileStorage methods '''

    def get_recording(self, attempt_id: str):
        tmp_file = f'{self.tmp_dir}/{attempt_id}.wav'
        self.download_file(attempt_id, self.recordings_dir, tmp_file)
        return tmp_file

    def remove_recordings(self, attempt_id_list):
        self.delete_files(attempt_id_list, self.recordings_dir)

    ''' IWaiverFileStorage methods '''

    def save_waiver(self, waiver_id: str, waiver_file: str):
        try:
            contents = open(waiver_file, 'rb')
        except FileNotFoundError as e:
            raise FileAccessException(f'{waiver_file} for waiver {waiver_id}', e)
        self.upload_file(waiver_id, self.waivers_dir, contents)

    def get_waiver(self, waiver_id: str):
        tmp_file = f'{self.tmp_dir}/{waiver_id}.pdf'
        self.download_file(waiver_id, self.waivers_dir, tmp_file)
        return tmp_file

    ''' Internal file access methods '''

    def upload_file(self, file_id: str, subdir: str, contents):
        try:
            self.s3.upload_fileobj(contents, self.bucket, subdir + file_id)
        except ClientError as e:
            raise FileAccessException(file_id, e)

    def download_file(self, file_id: str, subdir: str, download_path: str):
        try:
            self.s3.download_file(self.bucket, subdir + file_id, download_path)
        except ClientError as e:
            if e.response.get('Error', {}).get('Message') == 'Not Found':
                raise FileNotFoundException(file_id, e)
            else:
                raise S3ConnectionException(file_id, e)

    def delete_files(self, file_id_list, subdir: str):
        delete_objects = [{'Key': subdir + file_id} for file_id in file_id_list]
        try:
            self.s3.delete_objects(self.bucket, {'Objects': delete_objects})
        except ClientError as e:
            raise S3ConnectionException(file_id_list, e)
