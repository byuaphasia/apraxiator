from .iwaiverstorage import IWaiverStorage
from ...models import Waiver
from ...utils import IdGenerator, IdPrefix, EmailSender, PDFGenerator


class WaiverService(IdGenerator):
    def __init__(self, storage: IWaiverStorage, email_sender: EmailSender, pdf_generator: PDFGenerator):
        self.storage = storage
        self.email_sender = email_sender
        self.generator = pdf_generator

    def save_subject_waiver(self, user: str, subject_name: str, subject_email: str, clinician_email: str, date_signed: str, subject_signature_file):
        waiver_file = self.generator.generate_subject_waiver(
            subject_name, subject_email, date_signed, subject_signature_file
        )
        waiver_id = self.create_id(IdPrefix.WAIVER.value)
        waiver = Waiver(waiver_id, user, True, 'subject', subject_email, subject_name, date_signed, waiver_file, '', '')
        self.storage.add_waiver_to_storage(waiver)
        self.email_sender.send_subject_waiver(waiver_file, subject_email)
        self.email_sender.send_clinician_waiver(waiver_file, clinician_email, subject_name)

    def save_representative_waiver(self, user: str, subject_name: str, subject_email: str, clinician_email: str, date_signed: str, representative_name: str, relationship: str, representative_signature_file):
        waiver_file = self.generator.generate_representative_waiver(
            subject_name, subject_email, representative_name, relationship, date_signed, representative_signature_file
        )
        waiver_id = self.create_id(IdPrefix.WAIVER.value)
        waiver = Waiver(waiver_id, user, True, 'representative', subject_email, subject_name, date_signed, waiver_file, '', '')
        self.storage.add_waiver_to_storage(waiver)
        self.email_sender.send_subject_waiver(waiver_file, subject_email)
        self.email_sender.send_clinician_waiver(waiver_file, clinician_email, subject_name)

    def check_waivers(self, user: str, subject_name: str, subject_email: str):
        waiver = self.storage.get_valid_waiver(user, subject_name, subject_email)
        if waiver is not None:
            result = {
                'waiver': waiver.to_response()
            }
        else:
            result = {
                'waiver': None
            }
        return result

    def add_waiver(self, w: Waiver):
        related_waiver = self.get_valid_related_waiver(w.owner_id, w.subject_name, w.subject_email)
        if related_waiver is not None:
            self.refresh_waiver(related_waiver.id, w.date)
        else:
            self.storage.add_waiver_to_storage(w)

    def get_valid_related_waiver(self, user: str, subject_name: str, subject_email: str):
        return self.storage.get_valid_waiver(user, subject_name, subject_email)

    def invalidate_waiver(self, user: str, waiver_id: str):
        self.storage.check_is_owner_waiver(user, waiver_id)
        self.storage.update_waiver(waiver_id, 'valid', False)

    def refresh_waiver(self, waiver_id: str, date: str):
        self.storage.update_waiver(waiver_id, 'date', date)
        self.storage.update_waiver(waiver_id, 'valid', True)
