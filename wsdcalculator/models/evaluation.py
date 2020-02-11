class Evaluation:
    def __init__(self, id, age, gender, impression, owner_id, ambiance_threshold=None, date_created=None):
        self.id = id
        self.age = age
        self.gender = gender
        self.impression = impression
        self.owner_id = owner_id
        self.ambiance_threshold = ambiance_threshold
        self.date_created = date_created

    def to_list_response(self):
        return {
            'evaluationId': self.id,
            'age': self.age,
            'gender': self.gender,
            'impression': self.impression,
            'dateCreated': self.date_created
        }