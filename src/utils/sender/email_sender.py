import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import boto3
from botocore.exceptions import ClientError
from email.mime.application import MIMEApplication

from src.apraxiatorexception import ApraxiatorException
from src.utils.sender.isender import ISender


class EmailSender(ISender):
    def __init__(self, sender):
        self.sender = sender
        access_key = os.environ['APX_AWS_ACCESS']
        secret_key = os.environ['APX_AWS_SECRET']
        region = os.environ.get('APX_AWS_S3_REGION', 'us-west-2')
        self.client = boto3.client('ses', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

    def send_subject_waiver(self, waiver_file, to_email):
        subject = "Signed Copy of HIPAA Waiver"
        body_text = "Attached below is your signed copy of the HIPAA Waiver.\n\n"
        body_html = """\
        <html>
        <head></head>
        <body>
        <p>Attached below is your signed copy of the HIPAA Waiver.</p>
        </body>
        </html>
        """
        self.send_email(to_email, subject, body_text, body_html, waiver_file)

    def send_clinician_waiver(self, waiver_file, to_email, patient_name):
        subject = "HIPAA Waiver"
        body_text = "Attached below is a signed copy of the HIPAA Waiver for {}.\n\n".format(patient_name)
        body_html = """\
                <html>
                <head></head>
                <body>
                <p>Attached below is a signed copy of the HIPAA Waiver for {}.</p>
                </body>
                </html>
                """.format(patient_name)
        self.send_email(to_email, subject, body_text, body_html, waiver_file)

    def send_report(self, report_file, to_email, eval_id):
        subject = "WSD Test Report"
        body_text = "Attached below is the report for the evaluation {}.\n\n".format(eval_id)
        body_html = """\
            <html>
            <head></head>
            <body>
            <p>Attached below is the report for the evaluation {}.</p>
            </body>
            </html>
            """.format(eval_id)
        self.send_email(to_email, subject, body_text, body_html, report_file)

    def send_email(self, to_email, subject, body_text, body_html, attachment_file):
        charset = "utf-8"
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = to_email
        msg_body = MIMEMultipart('alternative')
        text_part = MIMEText(body_text.encode(charset), 'plain', charset)
        html_part = MIMEText(body_html.encode(charset), 'html', charset)
        msg_body.attach(text_part)
        msg_body.attach(html_part)
        att = MIMEApplication(open(attachment_file, 'rb').read())
        att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_file))
        msg.attach(msg_body)
        msg.attach(att)
        try:
            self.client.send_raw_email(
                Source=self.sender,
                Destinations=[to_email],
                RawMessage={'Data': msg.as_string()},
            )
        except ClientError:
            raise EmailSenderException()


class EmailSenderException(ApraxiatorException):
    def get_message(self):
        return "Error sending email"
