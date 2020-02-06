class Waiver:
    def __init__(self, res_name, res_email, date, filepath, signer, valid, rep_name=None, rep_relationship=None, id=None):
        self.id = id
        self.res_name = res_name
        self.res_email = res_email
        self.date = date
        self.filepath = filepath
        self.signer = signer
        self.valid = valid
        self.rep_name = rep_name
        self.rep_relationship = rep_relationship

    def to_response(self):
        return {
            'subjectName': self.res_name,
            'subjectEmail': self.res_email,
        }

    @staticmethod
    def from_row(row):
        id, res_name, res_email, rep_name, rep_relationship, date, signer, valid, filepath = row
        return Waiver(res_name, res_email, date, filepath, signer, valid, rep_name, rep_relationship, id)