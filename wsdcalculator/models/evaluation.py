class Evaluation:
    def __init__(self, id, owner_id, ambiance_threshold=None, date_created=None):
        self.id = id
        self.owner_id = owner_id
        self.ambiance_threshold = ambiance_threshold
        self.date_created = date_created