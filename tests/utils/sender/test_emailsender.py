import unittest

from ...context import src
from src.utils.sender.email_sender import EmailSender


class MockEmailSender(EmailSender):
    def __init__(self):
        self.to_email = ''
        self.subject = ''
        self.body_text = ''
        self.body_html = ''
        self.attachment_file = ''

    def send_email(self, to_email, subject, body_text, body_html, attachment_file):
        self.to_email = to_email
        self.subject = subject
        self.body_text = body_text
        self.body_html = body_html
        self.attachment_file = attachment_file


class TestEmailSender(unittest.TestCase):
    def test_send_subject_waiver(self):
        sender = MockEmailSender()
        file = 'waiver'
        recipient = 'subject'
        waiver_mention = 'HIPAA Waiver'
        sender.send_subject_waiver(file, recipient)
        self.assertTrue(waiver_mention in sender.body_text)
        self.assertTrue(waiver_mention in sender.body_html)
        self.assertTrue(waiver_mention in sender.subject)
        self.assertEqual(file, sender.attachment_file)
        self.assertEqual(recipient, sender.to_email)

    def test_send_clinician_waiver(self):
        sender = MockEmailSender()
        file = 'waiver'
        recipient = 'clinician'
        patient = 'patient'
        waiver_mention = 'HIPAA Waiver'
        sender.send_clinician_waiver(file, recipient, patient)
        self.assertTrue(waiver_mention in sender.body_text)
        self.assertTrue(waiver_mention in sender.body_html)
        self.assertTrue(waiver_mention in sender.subject)
        self.assertTrue(patient in sender.body_text)
        self.assertTrue(patient in sender.body_html)
        self.assertEqual(file, sender.attachment_file)
        self.assertEqual(recipient, sender.to_email)

    def test_send_report(self):
        sender = MockEmailSender()
        file = 'report'
        recipient = 'clinician'
        evaluation_id = 'EV-1'
        report_mention = 'report'
        sender.send_report(file, recipient, evaluation_id)
        self.assertTrue(report_mention in sender.body_text.lower())
        self.assertTrue(report_mention in sender.body_html.lower())
        self.assertTrue(report_mention in sender.subject.lower())
        self.assertTrue(evaluation_id in sender.body_text)
        self.assertTrue(evaluation_id in sender.body_html)
        self.assertEqual(file, sender.attachment_file)
        self.assertEqual(recipient, sender.to_email)
