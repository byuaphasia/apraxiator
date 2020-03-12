import logging

from ..services import IEvaluationStorage, IWaiverStorage
from .storageexceptions import ResourceNotFoundException, PermissionDeniedException, StorageException


class MemoryStorage(IEvaluationStorage, IWaiverStorage):
    def __init__(self):
        self.evaluations = {}
        self.attempts = {}
        self.waivers = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info('[event=memory-storage-started]')

    def is_healthy(self):
        return True

    ''' Evaluation Storage Methods '''

    def create_evaluation(self, e):
        self.evaluations[e.id] = e
        self.logger.info('[event=evaluation-added][evaluationId=%s]', e.id)

    def update_evaluation(self, id, field, value):
        e = self.evaluations.get(id, None)
        print(e)
        if e is not None:
            if field == 'ambiance_threshold':
                e.ambiance_threshold = value
                self.evaluations[id] = e
            else:
                self.logger.error(
                    '[event=update-evaluation-failure][evaluationId=%s][message=cannot update field "%s"]', id, field)
                raise StorageException()
        else:
            self.logger.error('[event=update-evaluation-error][evaluationId=%s][error=resource not found]', id)
            raise ResourceNotFoundException(id)

    def get_evaluation(self, id):
        e = self.evaluations.get(id, None)
        if e is not None:
            self.logger.info('[event=evaluation-retrieved][evaluationId=%s]', id)
            return e
        else:
            self.logger.error('[event=get-evaluation-error][evaluationId=%s][error=resource not found]', id)
            raise ResourceNotFoundException(id)

    def create_attempt(self, a):
        prev = self.attempts.get(a.evaluation_id, [])
        prev.append(a)
        self.attempts[a.evaluation_id] = prev
        self.logger.info('[event=attempt-added][evaluationId=%s][attemptId=%s][attemptCount=%s]',
                         a.evaluation_id, a.id, len(prev))

    def update_attempt(self, id, field, value):
        if field != 'active':
            self.logger.error('[event=update-attempt-failure][attemptId=%s][message=cannot update field "%s"]',
                              id, field)
            raise StorageException()
        for _, attempts in self.attempts.items():
            for a in attempts:
                if a.id == id:
                    a.active = value
                    return

    def list_evaluations(self, owner_id):
        evaluations = []
        for e in self.evaluations.values():
            if e.owner_id == owner_id:
                evaluations.append(e)
        self.logger.info('[event=evaluations-retrieved][ownerId=%s][evaluationCount=%s]', owner_id, len(evaluations))
        return evaluations

    def get_attempts(self, evaluation_id):
        attempts = self.attempts.get(evaluation_id, None)
        if attempts is not None:
            self.logger.info('[event=attempts-retrieved][evaluationId=%s][attemptCount=%s]',
                             evaluation_id, len(attempts))
            return attempts
        else:
            self.logger.error('[event=get-attempts-error][evaluationId=%s][error=resource not found]', evaluation_id)
            raise ResourceNotFoundException(id)

    def check_is_owner(self, owner_id, evaluation_id):
        e = self.evaluations.get(evaluation_id, None)
        if e is not None:
            if e.owner_id != owner_id:
                self.logger.error('[event=access-denied][evaluationId=%s][userId=%s]', evaluation_id, owner_id)
                raise PermissionDeniedException(evaluation_id, owner_id)
            else:
                self.logger.info('[event=owner-verified][evaluationId=%s][ownerId=%s]', evaluation_id, owner_id)
        else:
            self.logger.error('[event=check-owner-error][resourceId=%s][error=resource not found]', evaluation_id)
            raise ResourceNotFoundException(evaluation_id)

    def save_recording(self, attempt_id: str, recording):
        pass

    ''' Waiver Storage Methods '''

    def add_waiver_to_storage(self, w):
        self.waivers[w.id] = w

    def get_valid_waiver(self, user, subject_name, subject_email):
        for _, w in self.waivers.items():
            if subject_email == w.res_email and \
                    subject_name.lower() == w.res_name.lower() and \
                    w.valid and w.owner_id == user:
                return w
        return None

    def update_waiver(self, id, field, value):
        w = self.waivers[id]
        if field == 'date':
            w.date = value
        elif field == 'valid':
            w.valid = value
        self.waivers[id] = w

    def check_is_owner_waiver(self, user, waiver_id):
        w = self.waivers.get(waiver_id, None)
        if w is not None:
            if w.owner_id != user:
                self.logger.error('[event=access-denied][waiverId=%s][userId=%s]', waiver_id, user)
                raise PermissionDeniedException(waiver_id, user)
            else:
                self.logger.info('[event=owner-verified][evaluationId=%s][ownerId=%s]', waiver_id, user)
        else:
            self.logger.error('[event=check-owner-error][resourceId=%s][error=resource not found]', waiver_id)
            raise ResourceNotFoundException(id)
