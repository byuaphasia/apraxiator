class IPDFGenerator:
    def generate_subject_waiver(self, subject_name: str, subject_email: str, date_signed: str, signature_file):
        raise NotImplementedError()

    def generate_representative_waiver(self, subject_name: str, subject_email: str, representative_name: str, relationship: str, date_signed: str, signature_file):
        raise NotImplementedError()

    def generate_report(self, evaluation, attempts, name):
        raise NotImplementedError()
