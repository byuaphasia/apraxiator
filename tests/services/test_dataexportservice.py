import unittest
import zipfile
import pandas as pd
import os

from ...wsdcalculator.services import DataExportService, IDataExportStorage
from ...wsdcalculator.storage.storageexceptions import PermissionDeniedException
from ..utils import gen_export_data

admin = 'admin'
not_admin = 'not admin'
filename = 'exporttest'
num_rows = 3

class DummyDataExportStorage(IDataExportStorage):
    def export_data(self, start_date, end_date, user):
        if user != admin:
            raise PermissionDeniedException('export', user)
        return gen_export_data(num_rows)

s = DataExportService(DummyDataExportStorage())

class TestDataExportService(unittest.TestCase):
    def test_make_zip(self):
        contents = s.export('', '', admin)
        with open(filename, 'wb') as f:
            f.write(contents)
        self.assertTrue(zipfile.is_zipfile(filename))

    def test_make_csv(self):
        contents = s.export('', '', admin, False)
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