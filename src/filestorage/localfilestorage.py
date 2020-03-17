import os
import shutil

from ..services.evaluation import IEvaluationFileStorage
from ..services.dataexport import IDataExportFileStorage
from .exceptions import FileAccessException, FileNotFoundException


class LocalFileStorage(IEvaluationFileStorage, IDataExportFileStorage):
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
        self.tmp_dir = os.path.realpath(__file__ + '../../tmp/')

    ''' IEvaluationFileStorage methods '''

    def save_recording(self, attempt_id: str, recording):
        self.save_file(attempt_id, 'recordings', recording)

    ''' IDataExportFileStorage methods '''

    def get_recording(self, attempt_id: str):
        tmp_file = self.tmp_dir + attempt_id + '.wav'
        self.copy_file(attempt_id, 'recordings', tmp_file)
        return tmp_file

    def remove_recordings(self, attempt_id_list):
        for attempt_id in attempt_id_list:
            self.remove_file(attempt_id, 'recordings')

    ''' Internal file access methods '''

    def remove_file(self, file_id: str, dir_key: str):
        try:
            os.remove(self.dirs[dir_key] + f'/{file_id}')
        except IOError as e:
            raise FileAccessException(file_id, e)

    def save_file(self, file_id: str, dir_key: str, contents):
        try:
            with open(self.dirs[dir_key] + f'/{file_id}', 'wb') as f:
                f.write(contents)
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
