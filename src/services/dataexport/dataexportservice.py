import logging
from src.services.dataexport.idataexportstorage import IDataExportStorage
from src.services.dataexport.idataexportfilestorage import IDataExportFileStorage
from src.models.dataexport import DataExport, DataExportException
from src.storage.storageexceptions import PermissionDeniedException
from src.filestorage.exceptions import FileAccessException


class DataExportService:
    def __init__(self, storage: IDataExportStorage, file_store: IDataExportFileStorage):
        self.storage = storage
        self.file_store = file_store
        self.logger = logging.getLogger(__name__)

    def export(self, user, start_date, end_date, include_recordings=True, remove_recordings=False):
        self.confirm_export_access(user)
        data = self.storage.export_data(start_date, end_date)
        data_export = DataExport()

        attempt_id_list = []
        for row in data:
            try:
                attempt_id = data_export.add_row(row)
                if include_recordings:
                    try:
                        recording_file = self.file_store.get_recording(attempt_id)
                        data_export.add_recording(recording_file)
                        attempt_id_list.append(attempt_id)
                    except FileAccessException as e:
                        self.logger.info('[event=export-recording-failure][attemptId=%s][error=%r]', attempt_id, e)
            except DataExportException as e:
                self.logger.warning('[event=data-export-validation-error][error=%r][row=%s]',
                                    e, ':'.join([str(r) for r in row]))
        
        filename_base = f'{start_date}.{end_date}.'
        filename = filename_base + 'csv'
        data_export.to_csv(filename)
        if include_recordings:
            filename = filename_base + 'zip'
            data_export.to_zip(filename)
        
        contents = open(filename, 'rb').read()
        data_export.clean()
        if remove_recordings:
            self.file_store.remove_recordings(attempt_id_list)
        return contents

    def user_type(self, user):
        if self.storage.check_is_admin(user):
            return 'admin'
        else:
            return 'user'

    def confirm_export_access(self, user):
        if not self.storage.check_is_admin(user):
            raise PermissionDeniedException('export', user)
