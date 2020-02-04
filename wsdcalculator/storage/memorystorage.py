import logging

from .dbexceptions import WaiverAlreadyExists
from .evaluationstorage import EvaluationStorage
from .recordingstorage import RecordingStorage
from .waiverstorage import WaiverStorage
from .idgenerator import IdGenerator
from .storageexceptions import ResourceNotFoundException, PermissionDeniedException

class MemoryStorage(EvaluationStorage, RecordingStorage, WaiverStorage):
    def __init__(self):
        self.evaluations = {}
        self.attempts = {}
        self.waivers = {}
        self.logger = logging.getLogger(__name__)
    
    def _add_evaluation(self, e):
        self.evaluations[e.id] = e
        self.logger.info('[event=evaluation-added][evaluationId=%s]', e.id)

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

    def is_healthy(self):
        return True

    def add_waiver(self, w):
        for w_id, waiver in self.waivers.items():
            if w.res_name == waiver.res_name and w.res_email == waiver.res_email:
                self.update_waiver(w.res_name, w.res_email, w.date)
                raise WaiverAlreadyExists()
        if w.id is None:
            id_generator = IdGenerator()
            w.id = id_generator.create_id('waiver')
        self.waivers[w.id] = w

    def get_valid_waivers(self, res_name, res_email):
        valid_waivers = []
        for w_id, w in self.waivers.items():
            if res_name == w.res_name and res_email == w.res_email and w.valid:
                valid_waivers.append(w)
        return valid_waivers

    def update_waiver(self, res_name, res_email, date):
        for w_id, w in self.waivers.items():
            if res_name == w.res_name and res_email == w.res_email:
                self.waivers[w_id].date = date
        self.set_waiver_validity(res_name, res_email, True)

    def set_waiver_validity(self, res_name, res_email, validity):
        for w_id, w in self.waivers.items():
            if res_name == w.res_name and res_email == w.res_email:
                self.waivers[w_id].valid = validity
