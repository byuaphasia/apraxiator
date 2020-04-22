import unittest
import pytest
import json
import os
import soundfile as sf
from datetime import datetime

from ...context import src
from src.services.evaluation.calculators.voiceactivitydetector import VoiceActivityDetector

import pathlib, os
_file_path = pathlib.Path(__file__).parent.absolute()

test_dir_root = os.path.join(_file_path, '../../../apx-resources/recordings/')
test_results_dir = os.path.join(_file_path, '../../../apx-resources/test-results/')


@pytest.mark.skipif(not os.path.isdir(test_dir_root), reason='APX resources directory must be available')
class TestVad(unittest.TestCase):
    def setUp(self):
        filename = os.path.abspath(test_dir_root + 'testCases.json')
        self.test_cases = json.load(open(filename, 'r'))
        self.detector = VoiceActivityDetector()
        self.results = {}

    def test_measurements(self):
        for case in self.test_cases:
            basic_path = case['soundUri']
            
            speech_path = os.path.abspath(test_dir_root + basic_path)
            audio, sr = sf.read(speech_path)
            speech_duration = self.detector.measure(audio, sr, None)

            expected_duration = float(case['speechDuration'])

            r = {
                'expected': expected_duration,
                'actual': speech_duration
            }
            self.results[basic_path] = r

        for path, r in self.results.items():
            self.assertAlmostEqual(r['actual'], r['expected'], delta=350, msg='for file: {}'.format(path))

    def tearDown(self):
        filename = test_results_dir + 'vad' + datetime.now().isoformat() + '.json'
        json.dump(self.results, open(filename, 'w+'), indent=4)
