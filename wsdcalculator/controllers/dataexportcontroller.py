from flask import Request
from datetime import date
import logging

from ..services import DataExportService
from ..apraxiatorexception import InvalidRequestException

class DataExportController:
    def __init__(self, service: DataExportService):
        self.service = service
        self.logger = logging.getLogger(__name__)

    def handle_export(self, r: Request, user: str):
        self.logger.info('[event=export-data][user=%s]', user)
        start_date, end_date, include_recordings = self.get_request_data(r)
        self.validate_date_format(start_date)
        self.validate_date_format(end_date)
        self.validate_include_recordings(include_recordings)
        return self.service.export(user, start_date, end_date, include_recordings)

    # Validates that the date string passed in is in ISO YYYY-MM-DD format
    @staticmethod
    def validate_date_format(date_str: str):
        try:
            date.fromisoformat(date_str)
        except Exception as e:
            raise InvalidRequestException('Incorrect date format, expected YYYY-MM-DD', e)

    @staticmethod
    def validate_include_recordings(include_recordings):
        if not isinstance(include_recordings, bool):
            raise InvalidRequestException(f'includeRecordings is of type {type(include_recordings)}, expected a boolean')

    @staticmethod
    def get_request_data(r: Request):
        body = r.get_json(silent=True)
        if body is None:
            raise InvalidRequestException('Must provide JSON body')

        try:
            start_date = body['startDate']
            end_date = body['endDate']
        except KeyError as e:
            raise InvalidRequestException(f'Must provide {e.args[0]}', e)
        
        include_recordings = body.get('includeRecordings', True)

        return start_date, end_date, include_recordings