from flask import Request
from datetime import date

from ..services import DataExportService
from ..apraxiatorexception import InvalidRequestException

class DataExportController:
    def __init__(self, service: DataExportService):
        self.service = service

    def handle_export(self, r: Request, user: str):
        start_date, end_date, include_recordings = self.get_export_params(r)
        self.validate_date_format(start_date)
        self.validate_date_format(end_date)
        return self.service.export(start_date, end_date, user, include_recordings)

    # Validates that the date string passed in is in ISO YYYY-MM-DD format
    @staticmethod
    def validate_date_format(date_str: str):
        try:
            date.fromisoformat(date_str)
        except Exception as e:
            raise InvalidRequestException('Incorrect date format, expected YYYY-MM-DD', e)

    @staticmethod
    def get_export_params(r: Request):
        body = r.get_json(silent=True)
        if body is None:
            raise InvalidRequestException('Must provide JSON body')

        try:
            start_date = body['startDate']
            end_date = body['endDate']
        except KeyError as e:
            raise InvalidRequestException(f'Must provide {e.args[0]}', e)
        
        include_recordings = body.get('includeRecordings', True)
        if not isinstance(include_recordings, bool):
            raise InvalidRequestException(f'includeRecordings was {include_recordings}, expected a boolean')

        return start_date, end_date, include_recordings