import unittest
import pytest
import json
import os
from datetime import datetime

from ...context import src
from src.services.evaluation.calculators import WsdCalculatorBase
from src.utils import read_wav

results = {}
test_dir_root = '../apx-resources/recordings/'
test_results_dir = '../apx-resources/test-results/'


@pytest.mark.skipif(not os.path.isdir(test_dir_root), reason='APX resources directory must be available')
class TestWSDCalculator(unittest.TestCase):
    def setUp(self):
        filename = os.path.abspath(test_dir_root + 'testCases.json')
        self.test_cases = json.load(open(filename, 'r'))
        self.calculator = WsdCalculatorBase()

    def test_wsd_endpoint_finder(self):
        self.run_all_tests('endpoint', 70)

    def test_wsd_filterer(self):
        self.run_all_tests('filter', 100)

    def test_wsd_average(self):
        self.run_all_tests('average', 80)

    def run_all_tests(self, method, delta):
        tests = []
        for case in self.test_cases:
            base_path = case['soundUri']
            amb_path = test_dir_root + case['ambUri']
            speech_path = test_dir_root + case['speechUri']

            amb_audio, _ = read_wav(amb_path)
            audio, sr = read_wav(speech_path)
            threshold = self.calculator.get_ambiance_threshold(amb_audio)
            syllable_count = int(case['syllableCount'])

            expected_wsd = float(case['expectedWsd'])
            wsd, _ = self.calculator.calculate_wsd(audio, sr, syllable_count, method, threshold)
            tests.append((base_path, expected_wsd, wsd))

            r = results.get(base_path, {})
            tmp = {
                'expected': expected_wsd,
                f'{method}Actual': wsd,
                f'{method}Threshold': threshold
            }
            r.update(tmp)
            results[base_path] = r

        for path, expected, actual in tests:
            self.assertAlmostEqual(expected, actual, delta=delta, msg=path)

    @classmethod
    def tearDownClass(cls):
        filename = test_results_dir + 'calculateWsd' + datetime.now().isoformat() + '.json'
        json.dump(results, open(filename, 'w+'), indent=4)
