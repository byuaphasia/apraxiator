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
        prev = self.attempts.get(evaluation_id, [])
        prev.append(a)
        self.attempts[evaluation_id] = prev

    def get_attempts(self, evaluation_id):
        return self.attempts.get(evaluation_id, [])