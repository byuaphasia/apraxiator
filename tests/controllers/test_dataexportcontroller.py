import unittest

from ..context import src
from src.apraxiatorexception import InvalidRequestException
from src.controllers.dataexportcontroller import DataExportController
from ..testutils import DummyRequest, DummyAuth


class DummyDataExportService:
    def export(self, user, start_date, end_date, include_recordings):
        if user == 'admin':
            return True, True
        else:
            return False, False


auth = DummyAuth()
controller = DataExportController(auth, DummyDataExportService())

# Expected date format: YYYY-MM-DD
good_date = '2000-01-01'


class TestDataExportController(unittest.TestCase):
    def test_validate_date_format(self):
        controller.validate_date_format(good_date)

        with self.assertRaises(InvalidRequestException):
            controller.validate_date_format('2000-13-01')
        with self.assertRaises(InvalidRequestException):
            controller.validate_date_format('2000-12-1')
        with self.assertRaises(InvalidRequestException):
            controller.validate_date_format('2000.12.01')
        with self.assertRaises(InvalidRequestException):
            controller.validate_date_format('2000.02.30')
        with self.assertRaises(InvalidRequestException):
            controller.validate_date_format('not a date')

    def test_get_export_params(self):
        body = {
            'startDate': good_date,
            'endDate': good_date
        }
        req = DummyRequest()
        p0, p1, p2 = controller.get_request_data(req.set_body(body))
        self.assertEqual(good_date, p0)        
        self.assertEqual(good_date, p1)
        self.assertTrue(p2)

        with self.assertRaises(InvalidRequestException):
            controller.get_request_data(req.set_body(None))
        
        body['includeRecordings'] = True
        _, _, p2 = controller.get_request_data(req.set_body(body))
        self.assertTrue(p2)

        body['includeRecordings'] = False
        _, _, p2 = controller.get_request_data(req.set_body(body))
        self.assertFalse(p2)

        with self.assertRaises(InvalidRequestException):
            controller.get_request_data(req.set_body({}))

    def test_validate_include_recordings(self):
        controller.validate_include_recordings(True)
        controller.validate_include_recordings(False)
            
        with self.assertRaises(InvalidRequestException):
            controller.validate_include_recordings('not bool')

    def test_handle_export(self):
        auth.set_user('admin')
        body = {
            'startDate': good_date,
            'endDate': good_date
        }
        req = DummyRequest().set_body(body)
        self.assertTrue(controller.handle_export(req)[0])
        auth.set_user('not admin')
        self.assertFalse(controller.handle_export(req)[0])
