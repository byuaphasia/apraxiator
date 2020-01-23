import soundfile as sf
import numpy as np

def get_environment_percentile(env_recording, percentile=99.9):
    audio, _ = sf.read(env_recording)
    audio = np.abs(audio)
    return float(np.percentile(audio, percentile))