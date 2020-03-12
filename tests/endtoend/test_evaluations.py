import unittest
import os

from ...src.controllers import EvaluationController
from ...src.services import EvaluationService
from ...src.storage import MemoryStorage, SQLStorage
from ..utils import DummyRequest
from ...src.utils import IdPrefix, PDFGenerator, EmailSender

mode = os.environ.get('APX_TEST_MODE', 'mem')
if mode == 'db':
    storage = SQLStorage('test')
else:
    storage = MemoryStorage()


class DummyPDFGenerator(PDFGenerator):
    @staticmethod
    def _create_pdf(encoding, template_file_path, template_variables, outfile):
        pass


class DummyEmailSender(EmailSender):
    def send_email(self, to_email, subject, body_text, body_html, attachment_file):
        pass


service = EvaluationService(storage, DummyEmailSender(), DummyPDFGenerator())
controller = EvaluationController(service)


class TestEvaluations(unittest.TestCase):
    def test_create_evaluation(self):
        result = create_evaluation(controller, 'create')
        self.assertTrue('evaluationId' in result)
        self.assertEqual(IdPrefix.EVALUATION.value, result['evaluationId'][:2])

    def test_list_evaluations(self):
        num_evals = 5
        for _ in range(num_evals):
            create_evaluation(controller, 'list')
        result = controller.handle_list_evaluations(None, 'list')
        self.assertEqual(num_evals, len(result['evaluations']))

    def test_add_ambiance(self):
        create_result = create_evaluation(controller, 'amb')
        evaluation_id = create_result['evaluationId']
        result = add_ambiance(controller, 'amb', evaluation_id)
        self.assertDictEqual({}, result)

    def test_create_attempt(self):
        create_result = create_evaluation(controller, 'attempt')
        add_ambiance(controller, 'attempt', create_result['evaluationId'])
        result = create_attempt(controller, 'attempt', create_result['evaluationId'])
        self.assertEqual(IdPrefix.ATTEMPT.value, result['attemptId'][:2])
        self.assertAlmostEqual(188.6, result['wsd'], places=1)

    def test_get_attempts(self):
        create_result = create_evaluation(controller, 'get attempts')
        e_id = create_result['evaluationId']
        add_ambiance(controller, 'get attempts', e_id)
        num_atts = 5
        for _ in range(num_atts):
            create_attempt(controller, 'get attempts', e_id)
        result = controller.handle_get_attempts(None, 'get attempts', e_id)
        self.assertEqual(num_atts, len(result['attempts']))

    def test_update_attempt(self):
        e_id = create_evaluation(controller, 'update')['evaluationId']
        add_ambiance(controller, 'update', e_id)
        a_id = create_attempt(controller, 'update', e_id)['attemptId']
        body = {
            'active': False
        }
        r = DummyRequest().set_body(body)
        result = controller.handle_update_attempt(r, 'update', e_id, a_id)
        self.assertDictEqual({}, result)
        a = controller.handle_get_attempts(None, 'update', e_id)['attempts'][0]
        self.assertFalse(a['active'])

    def test_send_report(self):
        e_id = create_evaluation(controller, 'report')['evaluationId']
        add_ambiance(controller, 'report', e_id)
        active_id = create_attempt(controller, 'report', e_id)['attemptId']
        inactive_id = create_attempt(controller, 'report', e_id)['attemptId']
        update_body = {'active': False}
        update_r = DummyRequest().set_body(update_body)
        controller.handle_update_attempt(update_r, 'report', e_id, inactive_id)

        result = controller.handle_send_report(update_r, 'report', e_id)
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
            c = storage.db.cursor()
            c.execute('DROP TABLE recordings')
            c.execute('DROP TABLE waivers')
            c.execute('DROP TABLE attempts')
            c.execute('DROP TABLE evaluations')


def add_ambiance(c, user, evaluation_id):
    files = {
        'recording': open('tests/utils/exampleAmb.wav', 'rb')
    }
    r = DummyRequest().set_files(files)
    result = controller.handle_add_ambiance(r, user, evaluation_id)
    return result


def create_attempt(c, user, evaluation_id):
    files = {
        'recording': open('tests/utils/example.wav', 'rb')
    }
    values = {
        'word': 'gingerbread',
        'syllableCount': 3
    }
    r = DummyRequest().set_files(files).set_values(values)
    result = c.handle_create_attempt(r, user, evaluation_id)
    return result


def create_evaluation(c, user):
    body = {
        'age': '50',
        'gender': 'male', 
        'impression': 'normal'
    }
    r = DummyRequest().set_body(body)
    result = c.handle_create_evaluation(r, user)
    return result
