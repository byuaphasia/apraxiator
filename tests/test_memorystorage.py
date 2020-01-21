import unittest

from .context import MemoryStorage, PermissionDeniedException

storage = MemoryStorage()

class TestMemoryStorage(unittest.TestCase):
    def test_create_evaluation(self):
        evaluation_id = storage.create_evaluation(0, 'OWNER')
        self.assertEqual('EV-', evaluation_id[0:3])

    def test_fetch_evaluation(self):
        evaluation_id = storage.create_evaluation(0, 'OWNER')
        thresh = storage.fetch_evaluation(evaluation_id, 'OWNER')
        self.assertEqual(0, thresh)

        with self.assertRaises(PermissionDeniedException):
            storage.fetch_evaluation(evaluation_id, 'NOT THE OWNER')

    def test_create_attempt(self):
        evaluation_id = storage.create_evaluation(0, 'OWNER')
        attempt_id = storage.create_attempt(evaluation_id, 'word', 0, 0, 'OWNER')
        self.assertEqual('AT-', attempt_id[0:3])

        with self.assertRaises(PermissionDeniedException):
            storage.create_attempt(evaluation_id, 'word', 0, 0, 'NOT THE OWNER')

    def test_fetch_attempts(self):
        evaluation_id = storage.create_evaluation(0, 'OWNER')
        attempt_id = storage.create_attempt(evaluation_id, 'word', 0, 0, 'OWNER')
        attempts = storage.fetch_attempts(evaluation_id, 'OWNER')
        self.assertEqual(1, len(attempts))
        self.assertEqual(attempt_id, attempts[0].id)
        self.assertEqual(evaluation_id, attempts[0].evaluation_id)

        with self.assertRaises(PermissionDeniedException):
            storage.fetch_attempts(evaluation_id, 'NOT THE OWNER')
