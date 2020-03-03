import unittest

from ..wsdcalculator.models import Evaluation, Attempt
from ..wsdcalculator.storage import MemoryStorage
from ..wsdcalculator.storage.storageexceptions import ResourceNotFoundException

storage = MemoryStorage()

class TestMemoryStorage(unittest.TestCase):
    def test_create_evaluation(self):
        storage.create_evaluation(make_evaluation('create'))

    def test_get_evaluation(self):
        storage.create_evaluation(make_evaluation('get'))
        storage.update_evaluation('get', 'ambiance_threshold', 0)
        result = storage.get_evaluation('get')
        self.assertEqual(0, result.ambiance_threshold)

        with self.assertRaises(ResourceNotFoundException):
            storage.get_evaluation('bad')

    def test_list_evaluations(self):
        ids = []
        count = 5
        for i in range(count):
            storage.create_evaluation(make_evaluation(f'list{i}', 'list owner'))
            ids.append(f'list{i}')
        evaluations = storage.list_evaluations('list owner')
        self.assertEqual(count, len(evaluations))

        for e in evaluations:
            self.assertIn(e.id, ids)
            self.assertEqual('list owner', e.owner_id)

        empty_evaluations = storage.list_evaluations('owner of nothing')
        self.assertEqual(0, len(empty_evaluations))

    def test_create_attempt(self):
        storage.create_evaluation(make_evaluation('att'))
        storage.create_attempt(make_attempt('att', 'att'))

    def test_update_attempt(self):
        storage.create_evaluation(make_evaluation('att'))
        storage.create_attempt(make_attempt('att', 'att'))
        storage.update_attempt('att', 'active', False)
        attempts = storage.get_attempts('att')
        self.assertEqual('att', attempts[0].id)
        self.assertEqual(False, attempts[0].active)

    def test_fetch_attempts(self):
        storage.create_evaluation(make_evaluation('get atts'))
        ids = []
        count = 5
        for i in range(count):
            storage.create_attempt(make_attempt(f'att{i}', 'get atts'))
            ids.append(f'att{i}')
        attempts = storage.get_attempts('get atts')
        self.assertEqual(count, len(attempts))
        for a in attempts:
            self.assertIn(a.id, ids)
            self.assertEqual('get atts', a.evaluation_id)
            self.assertEqual(True, a.active)

def make_evaluation(id, owner='owner'):
    return Evaluation(id, '60', 'male', 'normal', owner)

def make_attempt(id, evaluation_id):
    return Attempt(id, evaluation_id, 'word', 0.0, 0.0, 0)