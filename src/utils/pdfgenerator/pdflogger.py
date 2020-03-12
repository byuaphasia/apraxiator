import logging

from .ipdfgenerator import IPDFGenerator


class PDFLogger(IPDFGenerator):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_subject_waiver(self, subject_name: str, subject_email: str, date_signed: str, signature_file):
        self.logger.info('[event=generate-subject-waiver][subjectName=%s][subjectEmail=%s][dateSigned=%s]',
                         subject_name, subject_email, date_signed)
        return ''

    def generate_representative_waiver(self, subject_name: str, subject_email: str, representative_name: str,
                                       relationship: str, date_signed: str, signature_file):
        self.logger.info('[event=generate-representative-waiver][subjectName=%s][subjectEmail=%s]' +
                         '[representativeName=%s][relationship=%s][dateSigned=%s]',
                         subject_name, subject_email, representative_name, relationship, date_signed)
        return ''

    def generate_report(self, evaluation, attempts, name):
        self.logger.info('[event=generate-report][name=%s][evaluation=%s][numAttempts=%s',
                         name, evaluation, len(attempts))
        return ''
