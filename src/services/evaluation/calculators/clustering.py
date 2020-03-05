import librosa

from .thresholddetector import ThresholdDetector


class Clusterer(ThresholdDetector):
    def get_speech_sample_count(self, audio, sr, threshold, **kwargs):
        num_clusters = kwargs.get('num_clusters', 24)
        segments = librosa.segment.agglomerative(audio, k=num_clusters)
        end = segments[-1]
        start = segments[1]
        return end - start
