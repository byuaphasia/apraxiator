from ..utils import IdGenerator, IdPrefix


class Waiver(IdGenerator):
    def __init__(self, id, owner_id, valid, signer, subject_email, subject_name, date, filepath,
                 representative_name=None, relationship=None):
        self.id = id
        self.subject_name = subject_name
        self.subject_email = subject_email
        self.date = date
        self.filepath = filepath
        self.signer = signer
        self.valid = valid
        self.representative_name = representative_name
        self.relationship = relationship
        self.owner_id = owner_id

    def to_response(self):
        return {
            'subjectName': self.subject_name,
            'subjectEmail': self.subject_email,
            'date': self.date,
            'waiverId': self.id
        }

    @staticmethod
    def from_row(row):
        id, subject_name, subject_email, representative_name, relationship, date, signer, valid, filepath, owner_id = row
        valid = bool(valid)
        return Waiver(id, owner_id, valid, signer, subject_email, subject_name, date, filepath, representative_name, relationship)
