class Attempt:
    def __init__(self, id, evaluation_id, word, wsd, duration, syllables, date_created=None, active=True):
        self.id = id
        self.evaluation_id = evaluation_id
        self.word = word
        self.wsd = wsd
        self.duration = duration
        self.date_created = date_created
        self.active = active
        self.syllables = syllables

    def to_response(self):
        r = {
            'attemptId': self.id,
            'evaluationId': self.evaluation_id,
            'word': self.word,
            'wsd': self.wsd,
            'duration': self.duration,
            'active': self.active,
            'dateCreated': self.date_created,
            'syllables': self.syllables
        }
        return r

    def to_report(self):
        r = {
            'word': self.word,
            'syllables': self.syllables,
            'wsd': self.wsd,
        }
        return r

    @staticmethod
    def from_row(row):
        evaluation_id, word, id, wsd, duration, active, date_created, syllables = row
        active = bool(active)
        return Attempt(id, evaluation_id, word, wsd, duration, syllables, date_created, active)
