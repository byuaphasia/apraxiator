import soundfile as sf
import numpy as np

from .thresholddetector import ThresholdDetector

class EndpointFinder(ThresholdDetector):
    def get_speech_sample_count(self, audio, threshold, sr):
        """ Calculates speech duration in milliseconds based off an associated environment threshold.
        Uses the threshold to find the start and end points of speech.

        Parameters:
        recording (str or file object): location of recording file or the file object itself
        syllable_count (int): number of syllables in the recorded word

        Returns:
        float: milliseconds of speech
        """
        start = self.find_start_point(audio, threshold, sr)
        end = self.find_end_point(audio, threshold, sr)
        return end - start

    def find_start_point(self, audio, threshold, sr, window_ratio=0.15, percentile=40):
        window = int(sr * window_ratio)
        start = -1
        for i in range(len(audio)):
            if audio[i] < threshold:
                continue
            if np.percentile(np.abs(audio[i:i+window]), percentile) > threshold:
                start = i
                break
        return start

    def find_end_point(self, audio, threshold, sr, window_ratio=0.15, percentile=40):
        window = int(sr * window_ratio)
        end = -1
        l = len(audio)
        for i in range(1, l + 1):
            if audio[l - i] < threshold:
                continue
            p = np.percentile(np.abs(audio[l-i-window:l-i]), percentile)
            if p > threshold:
                end = l - i
                break
        return end