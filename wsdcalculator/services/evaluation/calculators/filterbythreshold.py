import soundfile as sf
import numpy as np

from .thresholddetector import ThresholdDetector

class Filterer(ThresholdDetector):
    def get_speech_sample_count(self, audio, sr, threshold, **kwargs):
        """ Calculates speech duration in milliseconds based off an associated environment threshold.
        Smooths amplitude measurements and identifies speech by comparing it to that threshold.

        Parameters:
        audio (numpy array): array representing amplitude of audio
        threshold (float): amplitude threshold to filter by
        sr (int): sample rate, unused

        Returns:
        float: milliseconds of speech
        """
        is_above = np.where(audio > threshold, 1, 0)
        return np.sum(is_above)