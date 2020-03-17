import unittest
from os import path
import soundfile as sf
from numpy import ndarray

from ...src.filestorage import S3FileStorage, LocalFileStorage
from ...src.services.evaluation import IEvaluationFileStorage


class TestFileStorage(unittest.TestCase):
    def test_s3_save_recording(self):
        attempt_id = 'test s3 save recording'
        file_store = S3FileStorage('test')
        self.save_recording(file_store, attempt_id)
        filename = file_store.get_recording(attempt_id)
        audio, sr = sf.read(filename)
        self.assertTrue(isinstance(audio, ndarray))
        self.assertTrue(isinstance(sr, int))
        file_store.remove_recordings([attempt_id])

    def test_local_save_recording(self):
        attempt_id = 'test local save recording'
        file_store = LocalFileStorage()
        self.save_recording(file_store, attempt_id)
        filename = file_store.get_recording(attempt_id)
        audio, sr = sf.read(filename)
        self.assertTrue(isinstance(audio, ndarray))
        self.assertTrue(isinstance(sr, int))
        file_store.remove_recordings([attempt_id])

    @staticmethod
    def save_recording(file_store: IEvaluationFileStorage, attempt_id: str):
        file_path = path.realpath(__file__ + '../utils/example.wav')
        example_rec = open(file_path, 'rb')
        file_store.save_recording(attempt_id, example_rec)
