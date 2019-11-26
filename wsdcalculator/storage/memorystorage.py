import uuid

class MemoryStorage():
    def __init__(self):
        self.thresholds = {}
        self.attempts = {}
    
    def add_threshold(self, threshold):
        id = str(uuid.uuid4())
        self.thresholds[id] = threshold
        return id

    def get_threshold(self, id):
        return self.thresholds.get(id, -1)

    def add_attempt(self, id, term, attempt):
        prev = self.attempts.get(id, {})
        prev[term] = attempt
        self.attempts[id] = prev

    def get_attempts(self, id):
        return self.attempts.get(id, {})