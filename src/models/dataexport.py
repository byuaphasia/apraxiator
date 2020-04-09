import pandas as pd
import zipfile
import os
from datetime import datetime

from src.apraxiatorexception import ApraxiatorException


class DataExport:
    def __init__(self):
        self.data = []
        self.columns = [
            ('evaluationId', str),
            ('word', str),
            ('attemptId', str),
            ('wsd', float),
            ('duration', float),
            ('active', bool),
            ('syllableCount', int),
            ('dateCreated', datetime),
            ('age', str),
            ('gender', str),
            ('impression', str)
        ]
        self.files = []
        self.zipname = ''

    def add_row(self, row):
        row = self._validate_row(row)
        self.data.append(row)
        return row[self.columns.index(('attemptId', str))]

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
        if len(row) != len(self.columns):
            message = f'Row has {len(row)} items, expected {len(self.columns)}'
            raise DataExportException(message)
        for i in range(len(self.columns)):
            name, expected_type = self.columns[i]
            if expected_type == bool:
                row[i] = bool(row[i])
            if not isinstance(row[i], expected_type):
                message = f'Row value for column {name} was of type {type(row[i])}, expected {expected_type}'
                raise DataExportException(message)
        return row


class DataExportException(ApraxiatorException):
    def __init__(self, message, inner_error=None):
        super().__init__(inner_error)
        self.message = message

    def get_message(self):
        return f'Error on data export: {self.message}'
