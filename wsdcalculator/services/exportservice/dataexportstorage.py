class DataExportStorage:
    def export_data(self, start_date, end_date, user):
        self._confirm_export_access(user)
        return self._export_data(start_date, end_date)
    
    def _export_data(self, start_date, end_date):
        raise NotImplementedError

    def _confirm_export_access(self, user):
        raise NotImplementedError