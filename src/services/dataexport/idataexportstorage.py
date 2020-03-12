class IDataExportStorage:
    def export_data(self, start_date, end_date):
        raise NotImplementedError()

    def check_is_admin(self, user):
        raise NotImplementedError()
