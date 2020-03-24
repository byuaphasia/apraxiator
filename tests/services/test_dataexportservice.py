import unittest
import zipfile
import pandas as pd
import os
import shutil

from ..context import src
from src.services.dataexport.dataexportservice import DataExportService
from src.services.dataexport.idataexportfilestorage import IDataExportFileStorage
from src.services.dataexport.idataexportstorage import IDataExportStorage
from src.storage.storageexceptions import PermissionDeniedException
from ..testutils import gen_export_data

admin = 'admin'
not_admin = 'not admin'
filename = 'exporttest'
num_rows = 3


class DummyDataExportStorage(IDataExportStorage):
    def export_data(self, start_date, end_date):
        return gen_export_data(num_rows)
    
    def check_is_admin(self, user):
        if user != 'admin':
            return False
        else:
            return True


class DummyFileStore(IDataExportFileStorage):
    def __init__(self):
        self.idx = 0
        self.original = os.path.realpath(__file__ + '/../../testutils/example.wav')

    def get_recording(self, attempt_id: str):
        file_path = f'example-{self.idx}.wav'
        shutil.copy(self.original, file_path)
        self.idx += 1
        return file_path


s = DataExportService(DummyDataExportStorage(), DummyFileStore())


class TestDataExportService(unittest.TestCase):
    def test_make_zip(self):
        contents = s.export(admin, '', '')
        with open(filename, 'wb') as f:
            f.write(contents)
        self.assertTrue(zipfile.is_zipfile(filename))

    def test_make_csv(self):
        contents = s.export(admin, '', '', False)
        with open(filename, 'wb') as f:
            f.write(contents)
        self.assertFalse(zipfile.is_zipfile(filename))
        df = pd.read_csv(filename)
        self.assertEqual(num_rows, len(df))

    def test_not_admin(self):
        with self.assertRaises(PermissionDeniedException):
            s.export('', '', not_admin)

    @classmethod
    def tearDownClass(cls):
        os.remove(filename)
