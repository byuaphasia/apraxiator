import soundfile as sf
import numpy as np

class ThresholdDetector:
    num_milliseconds_per_second = 1000
    def __init__(self, storage):
        """
        evaluation_id (str): id connecting incoming recordings to an evaluation group
        """
        self.storage = storage

    def measure(self, audio, sr, evaluation_id, user_id, **kwargs):
        audio = self.smooth(audio)
        threshold = self.get_threshold(evaluation_id, user_id)
        num_speech_samples = self.get_speech_sample_count(audio, threshold, sr, **kwargs)
        num_speech_seconds = num_speech_samples / sr
        return num_speech_seconds * self.num_milliseconds_per_second

    def get_speech_sample_count(self, audio, threshold, sr, **kwargs):
        return -1

    def smooth(self, audio, window=20):
        smoothed = audio.copy()
        for i in range(window, len(audio) - window):
            smoothed[i] = np.max(np.abs(audio[i - window: i + window]))
        return smoothed

    def get_threshold(self, evaluation_id, user_id):
        return self.storage.fetch_evaluation(evaluation_id, user_id)