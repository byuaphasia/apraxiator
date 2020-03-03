from ..utils import IdGenerator, IdPrefix

class Waiver(IdGenerator):
    def __init__(self, res_name, res_email, date, filepath, signer, valid, rep_name=None, rep_relationship=None, id=None, owner_id=None):
        if id is None:
            id = self.create_id(IdPrefix.WAIVER.value)
        self.id = id
        self.res_name = res_name
        self.res_email = res_email
        self.date = date
        self.filepath = filepath
        self.signer = signer
        self.valid = valid
        self.rep_name = rep_name
        self.rep_relationship = rep_relationship
        self.owner_id = owner_id

    def to_response(self):
        return {
            'subjectName': self.res_name,
            'subjectEmail': self.res_email,
        }

    @staticmethod
    def from_row(row):
        id, res_name, res_email, rep_name, rep_relationship, date, signer, valid, filepath, owner_id = row
        valid = bool(valid)
        return Waiver(res_name, res_email, date, filepath, signer, valid, rep_name, rep_relationship, id, owner_id)
