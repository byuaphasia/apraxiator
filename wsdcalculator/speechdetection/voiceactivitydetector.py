import numpy as np
import uuid
import soundfile as sf
import librosa
import io
import webrtcvad

class VoiceActivityDetector:
    num_milliseconds_per_second = 1000
    def __init__(self, storage):
        """
        evaluation_id (str): id connecting incoming recordings to an evaluation group
        """
        self.storage = storage

    def measure(self, audio, sr, evaluation_id, user_id, **kwargs):
        num_speech_samples = self.get_speech_sample_count(audio, sr, **kwargs)
        num_speech_seconds = num_speech_samples / sr
        return num_speech_seconds * self.num_milliseconds_per_second

    def get_speech_sample_count(self, audio, sr, **kwargs):
        tmp_filename = 'tmp-' + str(uuid.uuid4())
        chunk_size = self._get_chunk_size(**kwargs)
        return 0

    def _get_chunk_size(self, new_sr=16000, num_ms=20, **kwargs):
        chunk_size = new_sr / self.num_milliseconds_per_second * num_ms * 2 # 2 bytes for 16bit file
        return int(chunk_size)

    def _resample_trim(self, filename, audio, sr, chunk_size, new_sr=16000, **kwargs):
        # Initial save
        sf.write(filename, audio, sr)
        # Load and save at new samplerate
        audio, sr = librosa.load(filename, sr=new_sr)
        librosa.output.write_wav(filename, audio, sr)
        # Load, trim, and save as 16-bit file
        audio, sr = sf.read(filename)
        overhang = len(audio) % chunk_size
        audio = audio[overhang//2: (overhang+1)//2]
        sf.write(filename, audio, sr)

    def _extract_data(self, filename, chunk_size):
        file = io.FileIO(filename, 'r')
        loc = 0
        chunk = file.read(4)
        # Skip until the 'data' section
        while chunk != b'data':
            loc += 1
            file.seek(loc)
            chunk = file.read(4)
        # Skip 'data' section meta
        loc += 8
        file.seek(loc)

        while True:
            chunk = file.read()
