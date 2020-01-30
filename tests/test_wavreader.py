import unittest
import soundfile as sf
import numpy as np
import os

from .context import read

test_filename = 'test.wav'
test_length = 20000
test_sr = 8000

class TestWavReader(unittest.TestCase):
    def test_mono(self):
        audio = np.zeros(test_length)
        sf.write(test_filename, audio, test_sr)
        audio, sr = read(test_filename)

        self.assertEqual(test_length, len(audio))
        self.assertEqual(1, len(audio.shape))
        self.assertEqual(test_sr, sr)

    def test_stereo(self):
        audio = np.zeros((test_length, 2))
        sf.write(test_filename, audio, test_sr)
        audio, sr = read(test_filename)

        self.assertEqual(test_length, len(audio))
        self.assertEqual(1, len(audio.shape))
        self.assertEqual(test_sr, sr)

    @classmethod
    def tearDownClass(cls):
        os.remove(test_filename)