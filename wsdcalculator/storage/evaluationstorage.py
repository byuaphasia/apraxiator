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
        self._update_evaluation(id, 'ambiance_threshold', threshold)

    def create_attempt(self, evaluation_id, word, wsd, duration, owner_id, syllables):
        self._check_is_owner(evaluation_id, owner_id)
        id = self.create_id('AT')
        a = Attempt(id, evaluation_id, word, wsd, duration, syllables)
        self._add_attempt(a)
        return id
    
    def update_active_attempt(self, evaluation_id, attempt_id, active, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        self._update_attempt(attempt_id, 'active', active)

    def fetch_threshold(self, id, owner_id):
        self._check_is_owner(id, owner_id)
        return self._get_threshold(id)
    
    def list_evaluations(self, owner_id):
        return self._get_evaluations(owner_id)

    def fetch_attempts(self, evaluation_id, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        return self._get_attempts(evaluation_id)

    def get_evaluation_report(self, evaluation_id, owner_id):
        self._check_is_owner(evaluation_id, owner_id)
        raw_attempts = self._get_active_attempts(evaluation_id)
        attempts = [a.to_report() for a in raw_attempts]
        evaluation_data = self._get_evaluation_data(evaluation_id)
        return {'attempts': attempts, 'date': evaluation_data['date'], 'gender': evaluation_data['gender'], 'age': evaluation_data['age'], 'impression': evaluation_data['impression']}

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

    def _update_attempt(self, id, field, value):
        raise NotImplementedException()

    def _get_evaluations(self, owner_id):
        raise NotImplementedException()

    def _get_attempts(self, evaluation_id):
        raise NotImplementedException()

    def _get_active_attempts(self, evaluation_id):
        raise NotImplementedException()

    def _get_evaluation_data(self, evaluation_id):
        raise NotImplementedException()
