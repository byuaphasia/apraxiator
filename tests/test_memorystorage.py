import unittest

from .context import MemoryStorage, PermissionDeniedException, ResourceNotFoundException

storage = MemoryStorage()

class TestMemoryStorage(unittest.TestCase):
    def test_create_evaluation(self):
        evaluation_id = storage.create_evaluation('60', 'male', 'normal', 'OWNER')
        self.assertEqual('EV-', evaluation_id[0:3])

    def test_fetch_threshold(self):
        evaluation_id = storage.create_evaluation('60', 'male', 'normal', 'OWNER')
        storage.add_threshold(evaluation_id, 0, 'OWNER')
        thresh = storage.fetch_threshold(evaluation_id, 'OWNER')
        self.assertEqual(0, thresh)

        with self.assertRaises(ResourceNotFoundException):
            storage.fetch_threshold(evaluation_id[:-1], 'OWNER')

        with self.assertRaises(PermissionDeniedException):
            storage.fetch_threshold(evaluation_id, 'NOT THE OWNER')

    def test_list_evaluations(self):
        ids = []
        count = 5
        for _ in range(count):
            ids.append(storage.create_evaluation('60', 'male', 'normal', 'LIST OWNER'))
        evaluations = storage.list_evaluations('LIST OWNER')
        self.assertEqual(count, len(evaluations))

        for e in evaluations:
            self.assertIn(e.id, ids)
            self.assertEqual('LIST OWNER', e.owner_id)

        empty_evaluations = storage.list_evaluations('OWNER OF NOTHING')
        self.assertEqual(0, len(empty_evaluations))

    def test_create_attempt(self):
        evaluation_id = storage.create_evaluation('60', 'male', 'normal', 'OWNER')
        attempt_id = storage.create_attempt(evaluation_id, 'word', 0, 0, 'OWNER')
        self.assertEqual('AT-', attempt_id[0:3])

        with self.assertRaises(PermissionDeniedException):
            storage.create_attempt(evaluation_id, 'word', 0, 0, 'NOT THE OWNER')

    def test_fetch_attempts(self):
        evaluation_id = storage.create_evaluation('60', 'male', 'normal', 'OWNER')
        attempt_id = storage.create_attempt(evaluation_id, 'word', 0, 0, 'OWNER')
        attempts = storage.fetch_attempts(evaluation_id, 'OWNER')
        self.assertEqual(1, len(attempts))
        self.assertEqual(attempt_id, attempts[0].id)
        self.assertEqual(evaluation_id, attempts[0].evaluation_id)

        with self.assertRaises(PermissionDeniedException):
            storage.fetch_attempts(evaluation_id, 'NOT THE OWNER')
