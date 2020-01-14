from .idgenerator import IdGenerator
from ..models.attempt import Attempt
from ..models.evaluation import Evaluation

class EvaluationStorage(IdGenerator):
    def __init__(self):
        self.thresholds = {}
        self.attempts = {}

    def is_healthy(self):
        return True
    
    def create_evaluation(self, threshold, owner_id):
        id = self.create_id('EV')
        e = Evaluation(id, owner_id, threshold)
        self._add_evaluation(e)
        return id

    def _add_evaluation(self, e):
        return -1

    def fetch_evaluation(self, id, owner_id):
        self._check_is_owner(id, owner_id)
        return self._get_threshold(id)

    def _get_threshold(self, id):
        return -1

    def create_attempt(self, evaluation_id, term, wsd, duration, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        id = self.create_id('AT')
        a = Attempt(id, evaluation_id, term, wsd, duration)
        self._add_attempt(a)
        return id

    def _add_attempt(self, a):
        return -1

    def fetch_attempts(self, evaluation_id, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        return self._get_attempts(evaluation_id)

    def _get_attempts(self, evaluation_id):
        return -1

    def _check_is_owner(self, evaluation_id, owner_id):
        return -1