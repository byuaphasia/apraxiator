import unittest
import json
import os
import soundfile as sf

from .context import voiceactivitydetector

class TestVad(unittest.TestCase):
    local_dir = os.path.dirname(__file__) + '/'
    recordings_dir = 'recordings/'
    def setUp(self):
        filename = os.path.abspath(self.local_dir + 'testCases.json')
        self.test_cases = json.load(open(filename, 'r'))
        self.detector = voiceactivitydetector.VoiceActivityDetector()
        self.results = {}

    def test_measurements(self):
        for case in self.test_cases:
            basic_path = case['soundUri']
            
            speech_path = os.path.abspath(self.local_dir + self.recordings_dir + basic_path)
            audio, sr = sf.read(speech_path)
            speech_duration = self.detector.measure(audio, sr, id, '')

            expected_duration = float(case['speechDuration'])

            r = {
                'expected': expected_duration,
                'actual': speech_duration
            }
            self.results[basic_path] = r

        for path, r in self.results.items():
            self.assertAlmostEqual(r['actual'], r['expected'], delta=350, msg='for file: {}'.format(path))

    def tearDown(self):
        json.dump(self.results, open('tests/vadTestResults.json', 'w+'), indent=4)