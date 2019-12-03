import unittest
import json
import os
import soundfile as sf

from .context import get_environment_percentile, memorystorage, findendpoints

class TestEndpointFinder(unittest.TestCase):
    local_dir = os.path.dirname(__file__) + '/'
    recordings_dir = 'recordings/'
    def setUp(self):
        filename = os.path.abspath(self.local_dir + 'testCases.json')
        self.test_cases = json.load(open(filename, 'r'))
        self.storage = memorystorage.MemoryStorage()
        self.detector = findendpoints.EndpointFinder(self.storage)
        self.results = {}

    def test_measurements_separate_env(self):
        for case in self.test_cases:
            basic_path = case['soundUri']

            amb_path = os.path.abspath(self.local_dir + self.recordings_dir + case['ambUri'])
            threshold = get_environment_percentile(amb_path)
            id = self.storage.create_evaluation(threshold, '')
            
            speech_path = os.path.abspath(self.local_dir + self.recordings_dir + case['speechUri'])
            audio, sr = sf.read(speech_path)
            speech_duration = self.detector.measure(audio, sr, id)

            expected_duration = float(case['speechDuration'])

            r = {
                'expected': expected_duration,
                'actual': speech_duration
            }
            self.results[basic_path] = r

        for path, r in self.results.items():
            self.assertAlmostEqual(r['actual'], r['expected'], delta=300, msg='for file: {}'.format(path))

    def tearDown(self):
        json.dump(self.results, open('tests/endpointFinderTestResults.json', 'w+'), indent=4)