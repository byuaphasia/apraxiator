import unittest
import soundfile as sf
import io
import numpy as np
import os

from .context import SQLStorage, PermissionDeniedException, Waiver, WaiverAlreadyExists

try:
    storage = SQLStorage()
except Exception:
    storage = None
owner_id = 'OWNER'
bad_owner_id = 'NOT THE OWNER'
sample_data = np.zeros(8000)

class TestSQLStorage(unittest.TestCase):
    def test_create_evaluation(self):
        evaluation_id = storage.create_evaluation(0, owner_id)
        self.assertEqual('EV-', evaluation_id[0:3])

    def test_fetch_evaluation(self):
        evaluation_id = storage.create_evaluation(0, owner_id)
        thresh = storage.fetch_evaluation(evaluation_id, owner_id)
        self.assertEqual(0, thresh)

        with self.assertRaises(PermissionDeniedException):
            storage.fetch_evaluation(evaluation_id, bad_owner_id)

    def test_create_attempt(self):
        evaluation_id = storage.create_evaluation(0, owner_id)
        attempt_id = storage.create_attempt(evaluation_id, 'word', 4, 12, owner_id)
        self.assertEqual('AT-', attempt_id[0:3])

        with self.assertRaises(PermissionDeniedException):
            storage.create_attempt(evaluation_id, 'word', 4, 12, bad_owner_id)

    def test_fetch_attempts(self):
        evaluation_id = storage.create_evaluation(0, owner_id)
        attempt_id = storage.create_attempt(evaluation_id, 'word', 4, 12, owner_id)
        attempts = storage.fetch_attempts(evaluation_id, owner_id)
        self.assertEqual(1, len(attempts))
        self.assertEqual(attempt_id, attempts[0].id)
        self.assertEqual(evaluation_id, attempts[0].evaluation_id)

        with self.assertRaises(PermissionDeniedException):
            storage.fetch_attempts(evaluation_id, bad_owner_id)

    def test_save_recording(self):
        evaluation_id = storage.create_evaluation(0, owner_id)
        attempt_id = storage.create_attempt(evaluation_id, 'word', 4, 12, owner_id)
        storage.save_recording(create_mock_recording(), evaluation_id, attempt_id, owner_id)

        with self.assertRaises(PermissionDeniedException):
            storage.save_recording(create_mock_recording(), evaluation_id, attempt_id, bad_owner_id)


    def test_get_recording(self):
        evaluation_id = storage.create_evaluation(0, owner_id)
        attempt_id = storage.create_attempt(evaluation_id, 'word', 4, 12, owner_id)
        storage.save_recording(create_mock_recording(), evaluation_id, attempt_id, owner_id)
        recording = storage.get_recording(evaluation_id, attempt_id, owner_id)

        data, sr = sf.read(io.BytesIO(recording))
        self.assertEqual(8000, sr)
        self.assertTrue(np.array_equal(sample_data, data))

    def test_add_waiver(self):
        waiver1 = Waiver('name', 'email', 'date', 'filepath', 'signer', True)
        storage.add_waiver(waiver1)
        waivers = storage.get_valid_waivers('name', 'email')
        self.assertEqual(1, len(waivers))
        self.assertDictEqual(waiver1.__dict__, waivers[0].__dict__)

        with self.assertRaises(WaiverAlreadyExists):
            waiver1.date = 'new date'
            storage.add_waiver(waiver1)

        waivers = storage.get_valid_waivers('name', 'email')
        self.assertEqual(1, len(waivers))
        self.assertEqual('new date', waivers[0].date)

    def test_invalidate_waiver(self):
        waiver = Waiver('the name', 'the email', 'date', 'filepath', 'signer', True)
        storage.add_waiver(waiver1)
        storage.invalidate_waiver('name', 'email')
        waivers = storage.get_valid_waivers('name', 'email')
        self.assertEqual(0, len(waivers))

    @classmethod
    def tearDownClass(cls):
        os.remove('test_wav.wav')

def create_mock_recording():
    sound = sf.SoundFile('test_wav.wav', mode='w', samplerate=8000, channels=1, format='WAV')
    sound.write(sample_data)
    return open('test_wav.wav', 'rb').read()
