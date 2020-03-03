class IDataExportStorage:
    def export_data(self, start_date, end_date):
        raise NotImplementedError()

    def confirm_export_access(self, user):
        raise NotImplementedError()