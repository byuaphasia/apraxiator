class Attempt:
    def __init__(self, id, evaluation_id, word, wsd, duration, date_created=None):
        self.id = id
        self.evaluation_id = evaluation_id
        self.word = word
        self.wsd = wsd
        self.duration = duration
        self.date_created = date_created

    def to_dict(self):
        r = {
            'attemptId': self.id,
            'evaluationId': self.evaluation_id,
            'word': self.word,
            'wsd': self.wsd,
            'duration': self.duration,
            'dateCreated': self.date_created
        }
        return r