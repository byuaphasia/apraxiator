import os
import shutil
import soundfile as sf

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
        self.tmp_dir = os.path.realpath('tmp')
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    ''' IEvaluationFileStorage methods '''

    def save_recording(self, attempt_id: str, audio, sr: int):
        try:
            filename = os.path.join(self.dirs['recordings'], attempt_id)
            sf.write(filename, audio, sr, format='WAV')
        except Exception as e:
            raise FileAccessException(attempt_id, e)

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
        filename = os.path.join(self.dirs['waivers'], waiver_id)
        if os.path.isfile(waiver_file):
            try:
                shutil.copy(waiver_file, filename)
            except Exception as e:
                raise FileAccessException(waiver_file, e)
        else:
            raise FileNotFoundException(waiver_file)

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

    def copy_file(self, file_id: str, dir_key: str, copy_file: str):
        file_path = self.dirs[dir_key] + f'/{file_id}'
        if os.path.isfile(file_path):
            try:
                shutil.copy(file_path, copy_file)
            except Exception as e:
                raise FileAccessException(file_id, e)
        else:
            raise FileNotFoundException(file_id)
