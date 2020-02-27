from .dataexportstorage import DataExportStorage
from ...models import DataExport

class DataExportService:
    def __init__(self, storage: DataExportStorage):
        self.storage = storage

    def export(self, start_date, end_date, user):
        data = self.storage.export_data(start_date, end_date)
        data_export = DataExport()