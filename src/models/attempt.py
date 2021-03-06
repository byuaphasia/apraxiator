from src.utils import TimeConversion


class Attempt:
    def __init__(self, id, evaluation_id, word, wsd, duration, syllable_count, date_created=None, active=True):
        self.id = id
        self.evaluation_id = evaluation_id
        self.word = word
        self.wsd = wsd
        self.duration = duration
        self.date_created = date_created
        self.active = active
        self.syllable_count = syllable_count

    def to_response(self):
        r = {
            'attemptId': self.id,
            'evaluationId': self.evaluation_id,
            'word': self.word,
            'wsd': self.wsd,
            'duration': self.duration,
            'active': self.active,
            'dateCreated': TimeConversion.to_response(self.date_created),
            'syllableCount': self.syllable_count
        }
        return r

    def to_report(self):
        r = {
            'word': self.word,
            'syllables': self.syllable_count,
            'wsd': self.wsd,
            'wsd_str': '{0:.2f}'.format(self.wsd)
        }
        return r

    @staticmethod
    def from_row(row):
        evaluation_id, word, id, wsd, duration, active, syllable_count, date_created = row
        active = bool(active)
        return Attempt(id, evaluation_id, word, wsd, duration, syllable_count, date_created, active)
