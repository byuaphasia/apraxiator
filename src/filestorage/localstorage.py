import os

from ..services.evaluation import IEvaluationFileStorage
from .exceptions import FileAccessException


class LocalStorage(IEvaluationFileStorage):
    def __init__(self):
        base_dir = os.path.dirname(os.path.realpath(__file__)) + '/files'
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
        self.dirs = {}
        for d in ['recordings', 'waivers']:
            full_path = base_dir + f'/{d}'
            if not os.path.isdir(full_path):
                os.mkdir(full_path)
            self.dirs[d] = full_path

    def save_recording(self, attempt_id: str, recording):
        self.save_file(attempt_id, 'recordings', recording)

    def remove_recording(self, attempt_id: str):
        self.remove_file(attempt_id, 'recordings')

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
