import os
import shutil

from src.services.waiver.iwaiverfilestorage import IWaiverFileStorage
from src.services.evaluation.ievaluationfilestorage import IEvaluationFileStorage
from src.services.dataexport.idataexportfilestorage import IDataExportFileStorage
from src.filestorage.exceptions import FileAccessException, FileNotFoundException


class LocalFileStorage(IEvaluationFileStorage, IDataExportFileStorage, IWaiverFileStorage):
    def __init__(self):
        base_dir = os.path.dirname(os.path.realpath(__file__)) + '/local'
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
        self.dirs = {}
        for d in ['recordings', 'waivers']:
            full_path = base_dir + f'/{d}'
            if not os.path.isdir(full_path):
                os.mkdir(full_path)
            self.dirs[d] = full_path
        self.tmp_dir = os.path.realpath(__file__ + '/../../tmp')
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    ''' IEvaluationFileStorage methods '''

    def save_recording(self, attempt_id: str, recording):
        self.save_file(attempt_id, 'recordings', recording)

    ''' IDataExportFileStorage methods '''

    def get_recording(self, attempt_id: str) -> str:
        tmp_file = f'{self.tmp_dir}/{attempt_id}.wav'
        self.copy_file(attempt_id, 'recordings', tmp_file)
        return tmp_file

    def remove_recordings(self, attempt_id_list):
        for attempt_id in attempt_id_list:
            self.remove_file(attempt_id, 'recordings')

    ''' IWaiverFileStorage methods '''

    def save_waiver(self, waiver_id: str, waiver_file: str):
        try:
            contents = open(waiver_file, 'rb')
        except FileNotFoundError as e:
            raise FileAccessException(f'{waiver_file} for waiver {waiver_id}', e)
        self.save_file(waiver_id, 'waivers', contents)

    def get_waiver(self, waiver_id: str) -> str:
        tmp_file = f'{self.tmp_dir}/{waiver_id}.pdf'
        self.copy_file(waiver_id, 'waivers', tmp_file)
        return tmp_file

    ''' Internal file access methods '''

    def remove_file(self, file_id: str, dir_key: str):
        try:
            os.remove(self.dirs[dir_key] + f'/{file_id}')
        except IOError as e:
            raise FileAccessException(file_id, e)

    def save_file(self, file_id: str, dir_key: str, contents):
        try:
            with open(self.dirs[dir_key] + f'/{file_id}', 'wb') as f:
                f.write(contents.read())
        except IOError as e:
            raise FileAccessException(file_id, e)

    def copy_file(self, file_id: str, dir_key: str, copy_file: str):
        file_path = self.dirs[dir_key] + f'/{file_id}'
        if os.path.isfile(file_path):
            try:
                shutil.copy(file_path, copy_file)
            except Exception as e:
                raise FileAccessException(file_id, e)
        else:
            raise FileNotFoundException(file_id)
