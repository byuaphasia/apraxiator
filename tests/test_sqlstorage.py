import unittest

import pytest
import numpy as np
import os
import uuid

from .context import src
from src.models.attempt import Attempt
from src.models.evaluation import Evaluation
from src.models.waiver import Waiver
from src.storage.sqlstorage import SQLStorage
from src.storage.dbexceptions import ConnectionException
from src.storage.storageexceptions import ResourceNotFoundException, IDAlreadyExists

try:
    storage = SQLStorage(name='test')
except ConnectionException:
    storage = None
owner_id = 'OWNER'
bad_owner_id = 'NOT THE OWNER'
sample_data = np.zeros(8000)


@pytest.mark.skipif(os.environ.get('APX_TEST_MODE', 'isolated') == 'isolated',
                    reason='Must not be running in "isolated" mode to access DB')
class TestSQLStorage(unittest.TestCase):
    def test_create_evaluation(self):
        storage.create_evaluation(make_evaluation('create'))

        storage.create_evaluation(make_evaluation('duplicate'))
        with self.assertRaises(IDAlreadyExists):
            storage.create_evaluation(make_evaluation('duplicate'))

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

        dup_id = 'dup att'
        storage.create_evaluation(make_evaluation(dup_id))
        storage.create_attempt(make_attempt(dup_id, dup_id))
        with self.assertRaises(IDAlreadyExists):
            storage.create_attempt(make_attempt(dup_id, dup_id))

    def test_update_attempt(self):
        storage.create_evaluation(make_evaluation('update'))
        storage.create_attempt(make_attempt('update', 'update'))
        storage.update_attempt('update', 'active', False)
        attempts = storage.get_attempts('update')
        self.assertEqual('update', attempts[0].id)
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

    def test_add_waiver(self):
        name = str(uuid.uuid4())
        waiver = Waiver('add waiver', owner_id=owner_id, valid=True, signer='signer',
                        subject_email='email', subject_name=name, date='date', filepath='filepath')
        storage.add_waiver(waiver)
        result = storage.get_valid_waiver(owner_id, name, 'email')
        self.assertDictEqual(waiver.__dict__, result.__dict__)

        with self.assertRaises(IDAlreadyExists):
            storage.add_waiver(waiver)

    def test_invalidate_waiver(self):
        name = str(uuid.uuid4())
        waiver = Waiver('invalidate waiver', owner_id=owner_id, valid=True, signer='signer',
                        subject_email='email', subject_name=name, date='date', filepath='filepath')
        storage.add_waiver(waiver)
        storage.update_waiver(waiver.id, 'valid', False)
        result = storage.get_valid_waiver(owner_id, name, 'email')
        self.assertIsNone(result)

    @classmethod
    def tearDownClass(cls):
        c = storage.db.cursor()
        c.execute('DROP TABLE waivers')
        c.execute('DROP TABLE attempts')
        c.execute('DROP TABLE evaluations')


def make_evaluation(id, owner='owner'):
    return Evaluation(id, '60', 'male', 'normal', owner)


def make_attempt(id, evaluation_id):
    return Attempt(id, evaluation_id, 'word', 0.0, 0.0, 0)
