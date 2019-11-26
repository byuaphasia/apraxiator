import uuid

class MemoryStorage():
    def __init__(self):
        self.memory = {}
    
    def add_threshold(self, threshold):
        id = str(uuid.uuid4())
        self.memory[id] = threshold
        return id

    def get_threshold(self, id):
        return self.memory.get(id, -1)