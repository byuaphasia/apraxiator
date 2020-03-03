import numpy as np
import logging

from .findendpoints import EndpointFinder
from .filterbythreshold import Filterer

class WsdCalculatorBase:
    def __init__(self):
        self.measurers = {
            'filter': Filterer(),
            'endpoint': EndpointFinder()
            # 'vad': VoiceActivityDetector()
        }
        self.logger = logging.getLogger(__name__)

    def calculate_wsd(self, audio, sr, syllable_count, method, threshold):
        self.logger.info('[event=calculate-wsd][method=%s]')
        m = self.measurers.get(method, None)
        # Default is to average all methods
        if m is None:
            total = 0
            for mes in self.measurers.values():
                total += mes.measure(audio, sr, threshold)
            duration = total / len(self.measurers)
        else:
            duration = m.measure(audio, sr, threshold)
            
        duration = float(duration)
        wsd = duration / syllable_count

        self.logger.info('[event=wsd-calculated][duration=%s][syllableCount=%s][wsd=%s]', duration, syllable_count, wsd)
        return wsd, duration

    @staticmethod
    def get_ambiance_threshold(audio, percentile=99.5):
        audio = np.abs(audio)
        return float(np.percentile(audio, percentile))