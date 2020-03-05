from .idataexportstorage import IDataExportStorage
from ...models import DataExport


class DataExportService:
    def __init__(self, storage: IDataExportStorage):
        self.storage = storage

    def export(self, user, start_date, end_date, include_recordings=True):
        self.storage.confirm_export_access(user)
        data = self.storage.export_data(start_date, end_date)
        data_export = DataExport()

        for row in data:
            data_export.add_row(row)
            if include_recordings:
                data_export.add_recording(row)
        
        filename_base = f'{start_date}.{end_date}.'
        filename = filename_base + 'csv'
        data_export.to_csv(filename)
        if include_recordings:
            filename = filename_base + 'zip'
            data_export.to_zip(filename)
        
        contents = open(filename, 'rb').read()
        data_export.clean()
        return contents
