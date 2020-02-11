from .idgenerator import IdGenerator
from ..models.attempt import Attempt
from ..models.evaluation import Evaluation
from ..apraxiatorexception import NotImplementedException

class EvaluationStorage(IdGenerator):
    def is_healthy(self):
        raise NotImplementedException()
    
    def create_evaluation(self, age, gender, impression, owner_id):
        id = self.create_id('EV')
        e = Evaluation(id, age, gender, impression, owner_id)
        self._add_evaluation(e)
        return id

    def add_threshold(self, id, threshold, owner_id):
        self._check_is_owner(id, owner_id)
        self._update_evaluation(id, 'threshold', threshold)

    def create_attempt(self, evaluation_id, word, wsd, duration, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        id = self.create_id('AT')
        a = Attempt(id, evaluation_id, word, wsd, duration)
        self._add_attempt(a)
        return id

    def fetch_threshold(self, id, owner_id):
        self._check_is_owner(id, owner_id)
        return self._get_threshold(id)
    
    def list_evaluations(self, owner_id):
        return self._get_evaluations(owner_id)

    def fetch_attempts(self, evaluation_id, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        return self._get_attempts(evaluation_id)


    ''' Abstract internal methods implemented by child classes '''

    def _check_is_owner(self, evaluation_id, owner_id):
        raise NotImplementedException()

    def _add_evaluation(self, e):
        raise NotImplementedException()

    def _update_evaluation(self, id, field, value):
        raise NotImplementedException()

    def _get_threshold(self, id):
        raise NotImplementedException()

    def _add_attempt(self, a):
        raise NotImplementedException()

    def _get_evaluations(self, owner_id):
        raise NotImplementedException()

    def _get_attempts(self, evaluation_id):
        raise NotImplementedException()
