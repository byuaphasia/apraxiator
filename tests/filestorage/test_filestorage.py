import unittest
import pytest
import os
import soundfile as sf
from numpy import ndarray

from ..context import src
from src.filestorage.s3filestorage import S3FileStorage
from src.filestorage.localfilestorage import LocalFileStorage
from src.services.evaluation.ievaluationfilestorage import IEvaluationFileStorage


class TestFileStorage(unittest.TestCase):
    @pytest.mark.skipif(os.environ.get('APX_TEST_MODE', 'isolated') == 'isolated',
                        reason='Must not be running in "isolated" mode to access S3')
    def test_s3_save_recording(self):
        attempt_id = 'test s3 save recording'
        file_store = S3FileStorage('test')
        self.save_recording(file_store, attempt_id)
        filename = file_store.get_recording(attempt_id)
        audio, sr = sf.read(filename)
        self.assertTrue(isinstance(audio, ndarray))
        self.assertTrue(isinstance(sr, int))
        file_store.remove_recordings([attempt_id])
        os.remove(filename)

    def test_local_save_recording(self):
        attempt_id = 'test local save recording'
        file_store = LocalFileStorage()
        self.save_recording(file_store, attempt_id)
        filename = file_store.get_recording(attempt_id)
        audio, sr = sf.read(filename)
        self.assertTrue(isinstance(audio, ndarray))
        self.assertTrue(isinstance(sr, int))
        file_store.remove_recordings([attempt_id])
        os.remove(filename)

    @staticmethod
    def save_recording(file_store: IEvaluationFileStorage, attempt_id: str):
        file_path = os.path.realpath(__file__ + '/../../utils/example.wav')
        example_rec = open(file_path, 'rb').read()
        file_store.save_recording(attempt_id, example_rec)
