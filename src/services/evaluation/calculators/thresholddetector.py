import numpy as np
import logging

from ....apraxiatorexception import NotImplementedException, ApraxiatorException
from .invalidsampleexceptions import SpeechDetectionException


class ThresholdDetector:
    num_milliseconds_per_second = 1000

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def measure(self, audio, sr, threshold, **kwargs):
        self.logger.info('[event=measuring-speech][method=%s]', self.__class__)
        try:
            audio = self.smooth(audio)
            num_speech_samples = self.get_speech_sample_count(audio, sr, threshold, **kwargs)
        except ApraxiatorException as e:
            raise e
        except Exception as e:
            self.logger.exception('[event=speech-detection-failure][method=%s]', self.__class__)
            raise SpeechDetectionException(e)

        num_speech_seconds = num_speech_samples / sr
        ms_speech = num_speech_seconds * self.num_milliseconds_per_second
        
        self.logger.info('[event=speech-measured][totalMs=%s][method=%s]', ms_speech, self.__class__)
        return ms_speech

    def get_speech_sample_count(self, audio, threshold, sr, **kwargs):
        raise NotImplementedException()

    def smooth(self, audio, window=20):
        smoothed = audio.copy()
        for i in range(window, len(audio) - window):
            smoothed[i] = np.max(np.abs(audio[i - window: i + window]))
        return smoothed
