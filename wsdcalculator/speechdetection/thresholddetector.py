import numpy as np
import logging

from ..apraxiatorexception import NotImplementedException, ApraxiatorException
from .invalidsampleexceptions import SpeechDetectionException

class ThresholdDetector:
    num_milliseconds_per_second = 1000
    def __init__(self, storage):
        """
        evaluation_id (str): id connecting incoming recordings to an evaluation group
        """
        self.storage = storage
        self.logger = logging.getLogger(__name__)

    def measure(self, audio, sr, evaluation_id, user_id, **kwargs):
        self.logger.info('[event=measuring-speech][evaluationId=%s]', evaluation_id)
        try:
            audio = self.smooth(audio)
            threshold = self.get_threshold(evaluation_id, user_id)
            num_speech_samples = self.get_speech_sample_count(audio, threshold, sr, **kwargs)
        except ApraxiatorException as e:
            raise e
        except Exception as e:
            self.logger.exception('[event=speech-detection-failure][evaluationId=%s]', evaluation_id)
            raise SpeechDetectionException(e)
        if num_speech_samples == -1:
            raise NotImplementedException()

        num_speech_seconds = num_speech_samples / sr
        ms_speech = num_speech_seconds * self.num_milliseconds_per_second
        
        self.logger.info('[event=speech-measured][evaluationId=%s][totalMs=%s]', evaluation_id, ms_speech)
        return ms_speech

    def get_speech_sample_count(self, audio, threshold, sr, **kwargs):
        return -1

    def smooth(self, audio, window=20):
        smoothed = audio.copy()
        for i in range(window, len(audio) - window):
            smoothed[i] = np.max(np.abs(audio[i - window: i + window]))
        return smoothed

    def get_threshold(self, evaluation_id, user_id):
        return self.storage.fetch_evaluation(evaluation_id, user_id)