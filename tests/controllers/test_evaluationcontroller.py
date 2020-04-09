import unittest
from unittest import mock

from ..context import src
from ..testutils.requestutils import DummyRequest
from src.controllers.evaluationcontroller import EvaluationController
from src.apraxiatorexception import InvalidRequestException


class Case:
    def __init__(self, user, body, error=False):
        self.user = user
        self.body = body
        self.error = error


class TestEvaluationController(unittest.TestCase):
    def setUp(self):
        self.auth = mock.Mock()
        self.service = mock.Mock()
        self.controller = EvaluationController(self.auth, self.service)

    def test_handle_create_evaluation(self):
        cases = [
            Case('missing age', {'impression': 'apraxia', 'gender': 'male'}, True),
            Case('int age', {'age': 50, 'impression': 'apraxia', 'gender': 'male'}, True),
            Case('long age', {'age': 'this age value is too long', 'impression': 'apraxia', 'gender': 'male'}, True),
            Case('valid', {'age': '50', 'impression': 'apraxia', 'gender': 'male'})
        ]
        self.service.create_evaluation.return_value = 'EV-1'
        for c in cases:
            self.auth.get_user.return_value = c.user
            r = DummyRequest().set_body(c.body)
            if c.error:
                with self.assertRaises(InvalidRequestException):
                    self.controller.handle_create_evaluation(r)
            else:
                result = self.controller.handle_create_evaluation(r)
                self.assertTrue('evaluationId' in result)
                self.assertEqual('EV-', result['evaluationId'][:3])
