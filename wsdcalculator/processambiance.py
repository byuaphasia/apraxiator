import numpy as np

from .wavreader.wavreader import read

def get_ambiance_threshold(ambiance_file, percentile=99.5):
    audio, _ = read(ambiance_file)
    audio = np.abs(audio)
    return float(np.percentile(audio, percentile))