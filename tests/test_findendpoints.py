import unittest
import json
import os
import soundfile as sf
from datetime import datetime
import numpy as np

from .context import get_ambiance_threshold, memorystorage, findendpoints, invalidsampleexceptions

test_dir_root = '../apx-resources/recordings/'
test_results_dir = '../apx-resources/test-results/'

class TestEndpointFinder(unittest.TestCase):
    def setUp(self):
        filename = os.path.abspath(test_dir_root + 'testCases.json')
        self.test_cases = json.load(open(filename, 'r'))
        self.storage = memorystorage.MemoryStorage()
        self.detector = findendpoints.EndpointFinder(self.storage)
        self.results = {}

    def test_measurements_separate_env(self):
        for case in self.test_cases:
            basic_path = case['soundUri']
            id = self.storage.create_evaluation('age', 'gender', 'impression', 'owner')

            amb_path = os.path.abspath(test_dir_root + case['ambUri'])
            threshold = get_ambiance_threshold(amb_path)
            self.storage.add_threshold(id, threshold, 'owner')
            
            speech_path = os.path.abspath(test_dir_root + case['speechUri'])
            audio, sr = sf.read(speech_path)
            speech_duration = self.detector.measure(audio, sr, id, 'owner')

            expected_duration = float(case['speechDuration'])

            r = {
                'expected': expected_duration,
                'actual': speech_duration
            }
            self.results[basic_path] = r

        for path, r in self.results.items():
            self.assertAlmostEqual(r['actual'], r['expected'], delta=200, msg='for file: {}'.format(path))

    def test_loud_threshold(self):
        threshold = 0.5
        audio = np.full(20000, 0.2)
        sr = 16000
        id = self.storage.create_evaluation('age', 'gender', 'impression', 'owner')
        self.storage.add_threshold(id, threshold, 'owner')

        with self.assertRaises(invalidsampleexceptions.InvalidSpeechSampleException):
            self.detector.measure(audio, sr, id, 'owner')

    def tearDown(self):
        filename = test_results_dir + 'findEndpoints' + datetime.now().isoformat() + '.json'
        json.dump(self.results, open(filename, 'w+'), indent=4)