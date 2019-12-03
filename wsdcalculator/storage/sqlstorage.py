from .evaluationstorage import EvaluationStorage

class SQLStorage(EvaluationStorage):
    def _add_evaluation(self, e):
        pass

    def _get_threshold(self, id):
        pass
    
    def _add_attempt(self, a):
        pass

    def _get_attempts(self, evaluation_id):
        pass

    def _check_is_owner(self, evaluation_id, owner_id):
        return True