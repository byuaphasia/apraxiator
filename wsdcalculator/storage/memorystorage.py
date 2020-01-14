import logging

from .evaluationstorage import EvaluationStorage
from .recordingstorage import RecordingStorage
from .storageexceptions import ResourceNotFoundException

class MemoryStorage(EvaluationStorage, RecordingStorage):
    def __init__(self):
        self.thresholds = {}
        self.attempts = {}
        self.logger = logging.getLogger(__name__)
    
    def _add_evaluation(self, e):
        self.thresholds[e.id] = e

    def _get_threshold(self, id):
        e = self.thresholds.get(id, None)
        if e is not None:
            t = e.ambiance_threshold
            self.logger.info('[event=get-threshold][evaluationId=%s][threshold=%s]', id, t)
            return t
        else:
            self.logger.error('[event=get-threshold-error][evaluationId=%s][error=resource not found]', id)
            raise ResourceNotFoundException(id)            

    def _add_attempt(self, a):
        prev = self.attempts.get(a.evaluation_id, [])
        prev.append(a)
        self.attempts[a.evaluation_id] = prev

    def _get_attempts(self, evaluation_id):
        return self.attempts.get(evaluation_id, [])