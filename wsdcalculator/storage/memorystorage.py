import logging

from .evaluationstorage import EvaluationStorage
from .recordingstorage import RecordingStorage
from .waiverstorage import WaiverStorage
from .idgenerator import IdGenerator
from .storageexceptions import ResourceNotFoundException, PermissionDeniedException, WaiverAlreadyExists, StorageException

class MemoryStorage(EvaluationStorage, RecordingStorage, WaiverStorage, IdGenerator):
    def __init__(self):
        self.evaluations = {}
        self.attempts = {}
        self.waivers = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info('[event=memory-storage-started]')
  
    def is_healthy(self):
        return True
  
    ''' Evaluation Storage Methods '''

    def _add_evaluation(self, e):
        self.evaluations[e.id] = e
        self.logger.info('[event=evaluation-added][evaluationId=%s]', e.id)

    def _update_evaluation(self, id, field, value):
        e = self.evaluations.get(id, None)
        if e is not None:
            if field == 'threshold':
                e.ambiance_threshold = value
                self.evaluations[id] = e 
            else:
                self.logger.error('[event=update-evaluation-failure][evaluationId=%s][message=cannot update field "%s"]', id, field)
                raise StorageException()
        else:
            self.logger.error('[event=update-evaluation-error][evaluationId=%s][error=resource not found]', id)
            raise ResourceNotFoundException(id)     

    def _get_threshold(self, id):
        e = self.evaluations.get(id, None)
        if e is not None:
            t = e.ambiance_threshold
            self.logger.info('[event=threshold-retrieved][evaluationId=%s][threshold=%s]', id, t)
            return t
        else:
            self.logger.error('[event=get-threshold-error][evaluationId=%s][error=resource not found]', id)
            raise ResourceNotFoundException(id)            

    def _add_attempt(self, a):
        prev = self.attempts.get(a.evaluation_id, [])
        prev.append(a)
        self.attempts[a.evaluation_id] = prev
        self.logger.info('[event=attempt-added][evaluationId=%s][attemptId=%s][attemptCount=%s]', a.evaluation_id, a.id, len(prev))

    def _get_evaluations(self, owner_id):
        evaluations = []
        for e in self.evaluations.values():
            if e.owner_id == owner_id:
                evaluations.append(e)
        self.logger.info('[event=evaluations-retrieved][ownerId=%s][evaluationCount=%s]', owner_id, len(evaluations))
        return evaluations

    def _get_attempts(self, evaluation_id):
        attempts = self.attempts.get(evaluation_id, None)
        if attempts is not None:
            self.logger.info('[event=attempts-retrieved][evaluationId=%s][attemptCount=%s]', evaluation_id, len(attempts))
            return attempts
        else:
            self.logger.error('[event=get-attempts-error][evaluationId=%s][error=resource not found]', evaluation_id)
            raise ResourceNotFoundException(id)

    def _check_is_owner(self, evaluation_id, owner_id):
        e = self.evaluations.get(evaluation_id, None)
        if e is not None:
            if e.owner_id != owner_id:
                self.logger.error('[event=access-denied][evaluationId=%s][userId=%s]', evaluation_id, owner_id)
                raise PermissionDeniedException(evaluation_id, owner_id)
            else:
                self.logger.info('[event=owner-verified][evaluationId=%s][ownerId=%s]', evaluation_id, owner_id)
        else:
            self.logger.error('[event=check-owner-error][resourceId=%s][error=resource not found]', evaluation_id)
            raise ResourceNotFoundException(id)

    ''' Waiver Storage Methods '''

    def _add_waiver(self, w):
        if w.id is None:
            w.id = self.create_id('WV')
        self.waivers[w.id] = w

    def get_valid_waivers(self, res_name, res_email):
        valid_waivers = []
        for _, w in self.waivers.items():
            if res_name == w.res_name and res_email == w.res_email and w.valid:
                valid_waivers.append(w)
        return valid_waivers

    def _update_waiver(self, id, field, value):
        w = self.waivers[id]
        if field == 'date':
            w.date = value
        elif field == 'valid':
            w.valid = value
        self.waivers[id] = w
