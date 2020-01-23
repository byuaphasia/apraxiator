import numpy as np

from .wavreader.wavreader import read

def get_environment_percentile(env_recording, percentile=99.9):
    audio, _ = read(env_recording)
    audio = np.abs(audio)
    return float(np.percentile(audio, percentile))