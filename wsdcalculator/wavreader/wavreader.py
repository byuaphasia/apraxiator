import soundfile as sf
import numpy as np
import logging

from ..apraxiatorexception import InvalidRequestException

logger = logging.getLogger(__name__)

def read(file_object):
    try:
        data, sr = sf.read(file_object)
    except Exception as e:
        logger.exception('[event=read-file-failure]')
        raise InvalidRequestException('Invalid WAV file provided', e)
    if len(data.shape) > 1:
        logger.info('[event=stereo-file-found][fileShape=%s]', data.shape)
        data = np.mean(data, axis=1)
    logger.info('[event=file-read][fileShape=%s][sampleRate=%s]', data.shape, sr)
    return data, sr