class Attempt:
    def __init__(self, id, evaluation_id, term, wsd, duration, date_created=None):
        self.id = id
        self.evaluation_id = evaluation_id
        self.term = term
        self.wsd = wsd
        self.duration = duration
        self.date_created = date_created