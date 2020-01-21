import unittest
import soundfile as sf
import io
import numpy as np

from .context import SQLStorage, PermissionDeniedException

storage = SQLStorage()
owner_id = 'OWNER'
bad_owner_id = 'NOT THE OWNER'
sample_data = np.asarray([1,2,3,4])

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
        attempt_id = storage.create_attempt(evaluation_id, 'word', 0, 0, owner_id)
        self.assertEqual('AT-', attempt_id[0:3])

        with self.assertRaises(PermissionDeniedException):
            storage.create_attempt(evaluation_id, 'word', 0, 0, bad_owner_id)

    def test_fetch_attempts(self):
        evaluation_id = storage.create_evaluation(0, owner_id)
        attempt_id = storage.create_attempt(evaluation_id, 'word', 0, 0, owner_id)
        attempts = storage.fetch_attempts(evaluation_id, owner_id)
        self.assertEqual(1, len(attempts))
        self.assertEqual(attempt_id, attempts[0].id)
        self.assertEqual(evaluation_id, attempts[0].evaluation_id)

        with self.assertRaises(PermissionDeniedException):
            storage.fetch_attempts(evaluation_id, bad_owner_id)

    def test_save_recording(self):
        evaluation_id = storage.create_evaluation(0, owner_id)
        attempt_id = storage.create_attempt(evaluation_id, 'word', 0, 0, owner_id)
        storage.save_recording(create_mock_recording(), evaluation_id, attempt_id, owner_id)

        with self.assertRaises(PermissionDeniedException):
            storage.save_recording(create_mock_recording(), evaluation_id, attempt_id, bad_owner_id)


    def test_get_recording(self):
        evaluation_id = storage.create_evaluation(0, owner_id)
        attempt_id = storage.create_attempt(evaluation_id, 'word', 0, 0, owner_id)
        storage.save_recording(create_mock_recording(), evaluation_id, attempt_id, owner_id)
        recording = storage.get_recording(evaluation_id, attempt_id, owner_id)
        data, sr = sf.read(recording)
        self.assertEqual(1, sr)
        self.assertTrue(np.array_equal(sample_data, data))

def create_mock_recording():
        file_object = io.BytesIO()
        sf.write(file_object, sample_data, samplerate=1)
        return file_object
