import numpy as np

from .thresholddetector import ThresholdDetector
from .invalidsampleexceptions import InvalidSpeechSampleException


class EndpointFinder(ThresholdDetector):
    def get_speech_sample_count(self, audio, sr, threshold, **kwargs):
        """ Calculates speech duration in milliseconds based off an associated environment threshold.
        Uses the threshold to find the start and end points of speech.

        Parameters:
        recording (str or file object): location of recording file or the file object itself
        syllable_count (int): number of syllables in the recorded word

        Returns:
        float: milliseconds of speech
        """
        window_ratio = kwargs.get('window_ratio', 0.1)
        percentile = kwargs.get('percentile', 30)

        start = self.find_start_point(audio, threshold, sr, window_ratio, percentile)
        end = self.find_end_point(audio, threshold, sr, window_ratio, percentile)
        return end - start

    def find_start_point(self, audio, threshold, sr, window_ratio, percentile):
        window = int(sr * window_ratio)
        start = -1
        for i in range(len(audio)-window):
            if audio[i] < threshold:
                continue
            if np.percentile(np.abs(audio[i:i+window]), percentile) > threshold:
                start = i
                break
        # In this case, no start point was found, so the threshold was louder than the recording sufficiently
        if start == -1:
            self.logger.error('[event=endpoint-not-found][threshold=%s][audioShape=%s]', threshold, audio.shape)
            raise InvalidSpeechSampleException('no start point of speech found')
        return start

    def find_end_point(self, audio, threshold, sr, window_ratio, percentile):
        reversed_audio = np.flip(audio)
        try:
            end = self.find_start_point(reversed_audio, threshold, sr, window_ratio, percentile)
        except InvalidSpeechSampleException:
            raise InvalidSpeechSampleException('no end point of speech found')
        return len(audio) - end
