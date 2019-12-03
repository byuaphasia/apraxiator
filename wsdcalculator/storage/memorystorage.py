from .evaluationstorage import EvaluationStorage

class MemoryStorage(EvaluationStorage):
    def __init__(self):
        self.thresholds = {}
        self.attempts = {}
    
    def _add_evaluation(self, e):
        self.thresholds[e.id] = e

    def _get_threshold(self, id):
        e = self.thresholds.get(id, None)
        if e is not None:
            return e.ambiance_threshold
        else:
            return -1

    def _add_attempt(self, a):
        prev = self.attempts.get(a.evaluation_id, [])
        prev.append(a)
        self.attempts[a.evaluation_id] = prev

    def _get_attempts(self, evaluation_id):
        return self.attempts.get(evaluation_id, [])