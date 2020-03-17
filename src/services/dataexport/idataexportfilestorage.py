class IDataExportFileStorage:
    def get_recording(self, attempt_id: str):
        raise NotImplementedError()

    def remove_recordings(self, attempt_id_list):
        raise NotImplementedError()
