import numpy as np
import uuid
import soundfile as sf
import librosa
import io
import webrtcvad
import logging
import os

class VoiceActivityDetector:
    num_milliseconds_per_second = 1000
    def __init__(self, storage=None):
        self.logger = logging.getLogger(__name__)

    def measure(self, audio, sr, evaluation_id, user_id, **kwargs):
        self.logger.info('[event=measuring-speech][evaluationId=%s]', evaluation_id)
        ms_speech = self.get_speech_sample_count(audio, sr, **kwargs)

        self.logger.info('[event=speech-measured][evaluationId=%s][totalMs=%s]', evaluation_id, ms_speech)
        return ms_speech

    def get_speech_sample_count(self, audio, sr, **kwargs):
        tmp_filename = 'tmp-' + str(uuid.uuid4())
        num_ms_per_chunk = kwargs.get('num_ms_per_chunk', 20)
        resample_rate = kwargs.get('resample_rate', 16000)
        vad_level = kwargs.get('vad_level', 3)

        chunk_size = self._get_chunk_size(num_ms_per_chunk, resample_rate)
        self._resample_trim(tmp_filename, audio, sr, chunk_size, resample_rate)
        data_chunks = self._extract_data(tmp_filename, chunk_size)
        os.remove(tmp_filename)

        num_voice_chunks = self._count_voice_chunks(data_chunks, resample_rate, vad_level)
        ms_voice = num_voice_chunks * num_ms_per_chunk
        return ms_voice

    def _count_voice_chunks(self, data, sr, vad_level):
        vad = webrtcvad.Vad(vad_level)
        count = 0
        for b in data:
            if vad.is_speech(b, sr):
                count += 1
        return count

    def _get_chunk_size(self, num_ms, new_sr):
        chunk_size = new_sr / self.num_milliseconds_per_second * num_ms * 2 # 2 bytes for 16bit file
        return int(chunk_size)

    def _resample_trim(self, filename, audio, sr, chunk_size, new_sr):
        # Initial save
        sf.write(filename, audio, sr, format='WAV')
        # Load and trim and save at new samplerate
        audio, sr = librosa.load(filename, sr=new_sr)
        overhang = len(audio) % chunk_size
        audio = audio[overhang//2: -(overhang+1)//2]
        sf.write(filename, audio, sr, format='WAV')
        self.logger.info('[event=audio-reformatted][tmpFilename=%s][newLength=%s][chunkSize=%s][resampleRate=%s]', filename, len(audio), chunk_size, new_sr)

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

        data_chunks = []
        while True:
            chunk = file.read(chunk_size)
            if len(chunk) == chunk_size:
                data_chunks.append(chunk)
            else:
                break
        
        self.logger.info('[event=data-bytes-extracted][numChunks=%s]', len(data_chunks))
        return data_chunks
