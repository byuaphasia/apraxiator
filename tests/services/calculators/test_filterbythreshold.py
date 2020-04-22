import unittest
import pytest
import json
import os
from datetime import datetime

from ...context import src
from src.services.evaluation.calculators import WsdCalculatorBase
from src.services.evaluation.calculators.filterbythreshold import Filterer
from src.utils import read_wav


import pathlib, os
_file_path = pathlib.Path(__file__).parent.absolute()

test_dir_root = os.path.join(_file_path, '../../../apx-resources/recordings/')
test_results_dir = os.path.join(_file_path, '../../../apx-resources/test-results/')


@pytest.mark.skipif(not os.path.isdir(test_dir_root), reason='APX resources directory must be available')
class TestEndpointFinder(unittest.TestCase):
    def setUp(self):
        filename = os.path.abspath(test_dir_root + 'testCases.json')
        self.test_cases = json.load(open(filename, 'r'))
        self.detector = Filterer()
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

    def tearDown(self):
        filename = test_results_dir + 'filterer' + datetime.now().isoformat() + '.json'
        json.dump(self.results, open(filename, 'w+'), indent=4)
