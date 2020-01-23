import unittest
import json
import os

from .context import WSDCalculator, memorystorage, get_environment_percentile

results = {}

class TestWSDCalculator(unittest.TestCase):
    local_dir = os.path.dirname(__file__) + '/'
    recordings_dir = 'recordings/'
    def setUp(self):
        filename = os.path.abspath(self.local_dir + 'testCases.json')
        self.test_cases = json.load(open(filename, 'r'))
        self.storage = memorystorage.MemoryStorage()
        self.calculator = WSDCalculator(self.storage)

    def test_wsd_endpoint_finder(self):
        for case in self.test_cases:
            basic_path = case['soundUri']

            amb_path = os.path.abspath(self.local_dir + self.recordings_dir + case['ambUri'])
            threshold = get_environment_percentile(amb_path)
            id = self.storage.create_evaluation(threshold, '')
            
            speech_path = os.path.abspath(self.local_dir + self.recordings_dir + case['speechUri'])
            syllable_count = int(case['syllableCount'])
            wsd, _ = self.calculator.calculate_wsd(speech_path, syllable_count, id, '', method='endpoint')

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
            self.assertAlmostEqual(r['endpointFinderActual'], r['expected'], delta=300, msg='for file: {}'.format(path))

    def test_wsd_filterer(self):
        for case in self.test_cases:
            basic_path = case['soundUri']

            amb_path = os.path.abspath(self.local_dir + self.recordings_dir + case['ambUri'])
            threshold = get_environment_percentile(amb_path)
            id = self.storage.create_evaluation(threshold, '')
            
            speech_path = os.path.abspath(self.local_dir + self.recordings_dir + case['speechUri'])
            syllable_count = int(case['syllableCount'])
            wsd, _ = self.calculator.calculate_wsd(speech_path, syllable_count, id, '', method='filter')

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
            self.assertAlmostEqual(r['filtererActual'], r['expected'], delta=300, msg='for file: {}'.format(path))

    def test_wsd_average(self):
        for case in self.test_cases:
            basic_path = case['soundUri']

            amb_path = os.path.abspath(self.local_dir + self.recordings_dir + case['ambUri'])
            threshold = get_environment_percentile(amb_path)
            id = self.storage.create_evaluation(threshold, '')
            
            speech_path = os.path.abspath(self.local_dir + self.recordings_dir + case['speechUri'])
            syllable_count = int(case['syllableCount'])
            wsd, _ = self.calculator.calculate_wsd(speech_path, syllable_count, id, '', method='average')

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
            self.assertAlmostEqual(r['averageActual'], r['expected'], delta=300, msg='for file: {}'.format(path))


    @classmethod
    def tearDownClass(cls):
        json.dump(results, open('tests/wsdCalculatorTestResults.json', 'w+'), indent=4)