from .idgenerator import IdGenerator
from ..models.attempt import Attempt
from ..models.evaluation import Evaluation
from ..apraxiatorexception import NotImplementedException

class EvaluationStorage(IdGenerator):
    def is_healthy(self):
        raise NotImplementedException()
    
    def create_evaluation(self, threshold, owner_id):
        id = self.create_id('EV')
        e = Evaluation(id, owner_id, threshold)
        self._add_evaluation(e)
        return id

    def _add_evaluation(self, e):
        raise NotImplementedException()

    def fetch_evaluation(self, id, owner_id):
        self._check_is_owner(id, owner_id)
        return self._get_threshold(id)

    def _get_threshold(self, id):
        raise NotImplementedException()

    def create_attempt(self, evaluation_id, word, wsd, duration, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        id = self.create_id('AT')
        a = Attempt(id, evaluation_id, word, wsd, duration)
        self._add_attempt(a)
        return id

    def _add_attempt(self, a):
        raise NotImplementedException()

    def fetch_attempts(self, evaluation_id, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        return self._get_attempts(evaluation_id)

    def _get_attempts(self, evaluation_id):
        raise NotImplementedException()

    def _check_is_owner(self, evaluation_id, owner_id):
        raise NotImplementedException()

    def save_recording(self, recording, evaluation_id, attempt_id, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        self._save_recording(recording, attempt_id)

    def get_recording(self, evaluation_id, attempt_id, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        return self._get_recording(attempt_id)

    def _save_recording(self, recording, attempt_id):
        raise NotImplementedException()

    def _get_recording(self, attempt_id):
        raise NotImplementedException()