import unittest
import json
import os
from datetime import datetime
import numpy as np

from ....src.services.evaluation.calculators import WsdCalculatorBase, InvalidSpeechSampleException
from ....src.services.evaluation.calculators.findendpoints import EndpointFinder
from ....src.utils import read_wav

test_dir_root = '../apx-resources/recordings/'
test_results_dir = '../apx-resources/test-results/'


class TestEndpointFinder(unittest.TestCase):
    def setUp(self):
        filename = os.path.abspath(test_dir_root + 'testCases.json')
        self.test_cases = json.load(open(filename, 'r'))
        self.detector = EndpointFinder()
        self.results = {}

    def test_measure(self):
        tests = []
        for case in self.test_cases:
            base_path = case['soundUri']
            amb_path = test_dir_root + case['ambUri']
            speech_path = test_dir_root + case['speechUri']

            amb_audio, _ = read_wav(amb_path)
            audio, sr = read_wav(speech_path)
            threshold = WsdCalculatorBase.get_ambiance_threshold(amb_audio)

            expected_duration = float(case['speechDuration'])
            duration = self.detector.measure(audio, sr, threshold)
            tests.append((base_path, expected_duration, duration))

            r = self.results.get(base_path, {})
            tmp = {
                'expected': expected_duration,
                'actual': duration,
            }
            r.update(tmp)
            self.results[base_path] = r

        for path, expected, actual in tests:
            self.assertAlmostEqual(expected, actual, delta=250, msg=path)

    def test_loud_threshold(self):
        threshold = 0.5
        audio = np.full(20000, 0.2)
        sr = 16000

        with self.assertRaises(InvalidSpeechSampleException):
            self.detector.measure(audio, sr, threshold)

    def tearDown(self):
        filename = test_results_dir + 'findEndpoints' + datetime.now().isoformat() + '.json'
        json.dump(self.results, open(filename, 'w+'), indent=4)
