import unittest
import soundfile as sf
import numpy as np
import os
import uuid

from ..src.models import Attempt, Evaluation, Waiver
from ..src.storage import SQLStorage
from ..src.storage.dbexceptions import ConnectionException
from ..src.storage.storageexceptions import ResourceNotFoundException, WaiverAlreadyExists

try:
    storage = SQLStorage(name='test')
except ConnectionException:
    storage = None
owner_id = 'OWNER'
bad_owner_id = 'NOT THE OWNER'
sample_data = np.zeros(8000)


class TestSQLStorage(unittest.TestCase):
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

    def test_save_recording(self):
        storage.create_evaluation(make_evaluation('rec'))
        storage.create_attempt(make_attempt('rec', 'rec'))
        storage.save_recording('rec', create_mock_recording())

    def test_add_waiver(self):
        name = str(uuid.uuid4())
        waiver = Waiver(name, 'email', 'date', 'filepath', 'signer', True, owner_id=owner_id)
        storage.add_waiver(waiver)
        waivers = storage.get_valid_waivers(name, 'email', owner_id)
        self.assertEqual(1, len(waivers))
        waiver.id = waivers[0].id
        self.assertDictEqual(waiver.__dict__, waivers[0].__dict__)

        with self.assertRaises(WaiverAlreadyExists):
            waiver.date = 'new date'
            storage.add_waiver(waiver)

        waivers = storage.get_valid_waivers(name, 'email', owner_id)
        self.assertEqual(1, len(waivers))
        self.assertEqual('new date', waivers[0].date)

    def test_invalidate_waiver(self):
        name = str(uuid.uuid4())
        waiver = Waiver(name, 'email', 'date', 'filepath', 'signer', True, owner_id=owner_id)
        storage.add_waiver(waiver)
        storage.invalidate_waiver(name, 'email', owner_id)
        waivers = storage.get_valid_waivers(name, 'email', owner_id)
        self.assertEqual(0, len(waivers))

    @classmethod
    def tearDownClass(cls):
        os.remove('test_wav.wav')
        c = storage.db.cursor()
        c.execute('DROP TABLE recordings')
        c.execute('DROP TABLE waivers')
        c.execute('DROP TABLE attempts')
        c.execute('DROP TABLE evaluations')


def create_mock_recording():
    sound = sf.SoundFile('test_wav.wav', mode='w', samplerate=8000, channels=1, format='WAV')
    sound.write(sample_data)
    return open('test_wav.wav', 'rb').read()


def make_evaluation(id, owner='owner'):
    return Evaluation(id, '60', 'male', 'normal', owner)


def make_attempt(id, evaluation_id):
    return Attempt(id, evaluation_id, 'word', 0.0, 0.0, 0)
