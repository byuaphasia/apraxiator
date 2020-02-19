import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import boto3
from botocore.exceptions import ClientError
from email.mime.application import MIMEApplication
from .waiversenderexception import WaiverSenderException


class WaiverSender:
    @staticmethod
    def send_patient_email(waiver_file, to_email):
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
        WaiverSender.send_email(to_email, subject, body_text, body_html, waiver_file)

    @staticmethod
    def send_clinician_email(waiver_file, to_email, patient_name):
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
        WaiverSender.send_email(to_email, subject, body_text, body_html, waiver_file)

    @staticmethod
    def send_email(to_email, subject, body_text, body_html, waiver_file):
        sender = "Tyson Harmon <projectapraxia@gmail.com>"
        aws_region = "us-west-2"
        charset = "utf-8"
        client = boto3.client('ses', region_name=aws_region)
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_email
        msg_body = MIMEMultipart('alternative')
        text_part = MIMEText(body_text.encode(charset), 'plain', charset)
        html_part = MIMEText(body_html.encode(charset), 'html', charset)
        msg_body.attach(text_part)
        msg_body.attach(html_part)
        att = MIMEApplication(open(waiver_file, 'rb').read())
        att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(waiver_file))
        msg.attach(msg_body)
        msg.attach(att)
        try:
            client.send_raw_email(
                Source=sender,
                Destinations=[to_email],
                RawMessage={'Data': msg.as_string()},
            )
        except ClientError:
            raise WaiverSenderException()
