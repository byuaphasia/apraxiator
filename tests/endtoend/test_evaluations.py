import unittest
import os

from ...src import ApraxiatorException
from ..utils import DummyRequest
from ...src.utils import IdPrefix, Factory


mode = os.environ.get('APX_TEST_MODE', 'mem')
factory = Factory.create_isolated_factory(mode)
controller = factory.ev_controller
attempts = []


class TestEvaluations(unittest.TestCase):
    def test_create_evaluation(self):
        factory.auth.user = 'create'
        result = create_evaluation(controller)
        self.assertTrue('evaluationId' in result)
        self.assertEqual(IdPrefix.EVALUATION.value, result['evaluationId'][:2])

    def test_list_evaluations(self):
        factory.auth.user = 'list'
        count = 5
        for _ in range(count):
            create_evaluation(controller)
        result = controller.handle_list_evaluations(None)
        self.assertEqual(count, len(result['evaluations']))

    def test_add_ambiance(self):
        factory.auth.user = 'amb'
        create_result = create_evaluation(controller)
        evaluation_id = create_result['evaluationId']
        result = add_ambiance(controller, evaluation_id)
        self.assertDictEqual({}, result)

    def test_create_attempt(self):
        factory.auth.user = 'attempt'
        create_result = create_evaluation(controller)
        add_ambiance(controller, create_result['evaluationId'])
        result = create_attempt(controller, create_result['evaluationId'])
        self.assertEqual(IdPrefix.ATTEMPT.value, result['attemptId'][:2])
        self.assertAlmostEqual(188.6, result['wsd'], places=1)

    def test_get_attempts(self):
        factory.auth.user = 'get attempts'
        create_result = create_evaluation(controller)
        e_id = create_result['evaluationId']
        add_ambiance(controller, e_id)
        num_atts = 5
        for _ in range(num_atts):
            create_attempt(controller, e_id)
        result = controller.handle_get_attempts(None, evaluation_id=e_id)
        self.assertEqual(num_atts, len(result['attempts']))

    def test_update_attempt(self):
        factory.auth.user = 'update'
        e_id = create_evaluation(controller)['evaluationId']
        add_ambiance(controller, e_id)
        a_id = create_attempt(controller, e_id)['attemptId']
        body = {
            'active': False
        }
        r = DummyRequest().set_body(body)
        result = controller.handle_update_attempt(r, evaluation_id=e_id, attempt_id=a_id)
        self.assertDictEqual({}, result)
        a = controller.handle_get_attempts(None, evaluation_id=e_id)['attempts'][0]
        self.assertFalse(a['active'])

    def test_send_report(self):
        factory.auth.user = 'report'
        e_id = create_evaluation(controller)['evaluationId']
        add_ambiance(controller, e_id)
        active_id = create_attempt(controller, e_id)['attemptId']
        inactive_id = create_attempt(controller, e_id)['attemptId']
        update_body = {'active': False}
        update_r = DummyRequest().set_body(update_body)
        controller.handle_update_attempt(update_r, evaluation_id=e_id, attempt_id=inactive_id)
        send_report_body = {
            'email': 'eamil',
            'name': 'name'
        }
        send_r = DummyRequest().set_body(send_report_body)
        result = controller.handle_send_report(send_r, evaluation_id=e_id)
        self.assertTrue('attempts' in result)
        self.assertTrue('evaluation' in result)
        self.assertTrue('dateCreated' in result['evaluation'])
        self.assertTrue('age' in result['evaluation'])
        self.assertTrue('gender' in result['evaluation'])
        self.assertTrue('impression' in result['evaluation'])
        self.assertEqual(1, len(result['attempts']))

    @classmethod
    def tearDownClass(cls):
        if mode == 'db':
            c = factory.storage.db.cursor()
            c.execute('DROP TABLE recordings')
            c.execute('DROP TABLE waivers')
            c.execute('DROP TABLE attempts')
            c.execute('DROP TABLE evaluations')
        for a in attempts:
            try:
                factory.file_store.remove_recording(a)
            except ApraxiatorException:
                pass


def add_ambiance(c, evaluation_id):
    files = {
        'recording': open('tests/utils/exampleAmb.wav', 'rb')
    }
    r = DummyRequest().set_files(files)
    result = c.handle_add_ambiance(r, evaluation_id=evaluation_id)
    return result


def create_attempt(c, evaluation_id):
    files = {
        'recording': open('tests/utils/example.wav', 'rb')
    }
    values = {
        'word': 'gingerbread',
        'syllableCount': 3
    }
    r = DummyRequest().set_files(files).set_values(values)
    result = c.handle_create_attempt(r, evaluation_id=evaluation_id)
    attempts.append(result['attemptId'])
    return result


def create_evaluation(c):
    body = {
        'age': '50',
        'gender': 'male', 
        'impression': 'normal'
    }
    r = DummyRequest().set_body(body)
    result = c.handle_create_evaluation(r)
    return result
