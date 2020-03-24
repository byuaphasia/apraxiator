import pandas as pd
import zipfile
import os

from .modelexceptions import DataExportException


class DataExport:
    def __init__(self):
        self.data = []
        self.columns = [
            ('evaluationId', str),
            ('word', str),
            ('attemptId', str),
            ('wsd', float),
            ('duration', float),
            ('dateCreated', str),
            ('age', str),
            ('gender', str),
            ('impression', str)
        ]
        self.files = []
        self.zipname = ''

    def add_row(self, row):
        self._validate_row(row)
        row = row[:-1]
        self.data.append(row)

    def add_recording(self, recording_file: str):
        self.files.append(recording_file)

    def to_csv(self, filename):
        try:
            df = pd.DataFrame.from_records(self.data, columns=[i[0] for i in self.columns])
            df.to_csv(filename, index=False)
            self.files.append(filename)
        except Exception as e:
            raise DataExportException('Problem saving data as csv', e)

    def to_zip(self, filename):
        try:
            z = zipfile.ZipFile(filename, 'w')
            for f in self.files:
                z.write(f)
            z.close()
            self.zipname = filename
        except Exception as e:
            raise DataExportException('Problem saving data as zip', e)

    def clean(self):
        try:
            if self.zipname != '':
                os.remove(self.zipname)
            for f in self.files:
                os.remove(f)
            self.zipname = ''
            self.files = []
        except Exception as e:
            raise DataExportException('Problem cleaning up export files', e)

    def _validate_row(self, row):
        # TODO: adjust to remove recordings table
        if len(row) != len(self.columns)+1:
            message = f'Row has {len(row)} items, expected {len(self.columns)+1}'
            raise DataExportException(message)
        for i in range(len(self.columns)):
            name, expected_type = self.columns[i]
            if not isinstance(row[i], expected_type):
                message = f'Row value for column {name} was of type {type(row[i])}, expected {expected_type}'
                raise DataExportException(message)
