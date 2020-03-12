import logging

from .isender import ISender


class LogSender(ISender):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def send_subject_waiver(self, waiver_file, recipient: str):
        self.logger.info('[event=log-send-subject-waiver][recipient=%s]', recipient)

    def send_clinician_waiver(self, waiver_file, recipient: str, patient_name: str):
        self.logger.info('[event=log-send-clinician-waiver][recipient=%s]', recipient)

    def send_report(self, report_file, recipient: str, evaluation_id: str):
        self.logger.info('[event=log-send-report][recipient=%s]', recipient)
