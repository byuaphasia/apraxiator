import unittest
import json
import os
from datetime import datetime

from .context import WSDCalculator, memorystorage, get_ambiance_threshold

results = {}
test_dir_root = '../apx-resources/recordings/'
test_results_dir = '../apx-resources/test-results/'

class TestWSDCalculator(unittest.TestCase):
    def setUp(self):
        filename = os.path.abspath(test_dir_root + 'testCases.json')
        self.test_cases = json.load(open(filename, 'r'))
        self.storage = memorystorage.MemoryStorage()
        self.calculator = WSDCalculator(self.storage)

    def test_wsd_endpoint_finder(self):
        for case in self.test_cases:
            basic_path = case['soundUri']
            id = self.storage.create_evaluation('age', 'gender', 'impression', 'owner')

            amb_path = os.path.abspath(test_dir_root + case['ambUri'])
            threshold = get_ambiance_threshold(amb_path)
            self.storage.add_threshold(id, threshold, 'owner')
            
            speech_path = os.path.abspath(test_dir_root + case['speechUri'])
            syllable_count = int(case['syllableCount'])
            wsd, _ = self.calculator.calculate_wsd(speech_path, syllable_count, id, 'owner', method='endpoint')

            expected_wsd = float(case['expectedWsd'])

            r = results.get(basic_path, {})
            tmp = {
                'expected': expected_wsd,
                'endpointFinderActual': wsd,
                'endpointThreshold': threshold
            }
            r.update(tmp)
            results[basic_path] = r

        for path, r in results.items():
            self.assertAlmostEqual(r['endpointFinderActual'], r['expected'], delta=75, msg='for file: {}'.format(path))

    def test_wsd_filterer(self):
        for case in self.test_cases:
            basic_path = case['soundUri']
            id = self.storage.create_evaluation('age', 'gender', 'impression', 'owner')

            amb_path = os.path.abspath(test_dir_root + case['ambUri'])
            threshold = get_ambiance_threshold(amb_path)
            self.storage.add_threshold(id, threshold, 'owner')
            
            speech_path = os.path.abspath(test_dir_root + case['speechUri'])
            syllable_count = int(case['syllableCount'])
            wsd, _ = self.calculator.calculate_wsd(speech_path, syllable_count, id, 'owner', method='filter')

            expected_wsd = float(case['expectedWsd'])

            r = results.get(basic_path, {})
            tmp = {
                'expected': expected_wsd,
                'filtererActual': wsd,
                'filtererThreshold': threshold
            }
            r.update(tmp)
            results[basic_path] = r

        for path, r in results.items():
            self.assertAlmostEqual(r['filtererActual'], r['expected'], delta=100, msg='for file: {}'.format(path))

    def test_wsd_average(self):
        for case in self.test_cases:
            basic_path = case['soundUri']
            id = self.storage.create_evaluation('age', 'gender', 'impression', 'owner')

            amb_path = os.path.abspath(test_dir_root + case['ambUri'])
            threshold = get_ambiance_threshold(amb_path)
            self.storage.add_threshold(id, threshold, 'owner')
            
            speech_path = os.path.abspath(test_dir_root + case['speechUri'])
            syllable_count = int(case['syllableCount'])
            wsd, _ = self.calculator.calculate_wsd(speech_path, syllable_count, id, 'owner', method='average')

            expected_wsd = float(case['expectedWsd'])

            r = results.get(basic_path, {})
            tmp = {
                'expected': expected_wsd,
                'averageActual': wsd,
                'averageThreshold': threshold
            }
            r.update(tmp)
            results[basic_path] = r

        for path, r in results.items():
            self.assertAlmostEqual(r['averageActual'], r['expected'], delta=100, msg='for file: {}'.format(path))


    @classmethod
    def tearDownClass(cls):
        filename = test_results_dir + 'calculateWsd' + datetime.now().isoformat() + '.json'
        json.dump(results, open(filename, 'w+'), indent=4)