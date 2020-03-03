import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import boto3
from botocore.exceptions import ClientError
from email.mime.application import MIMEApplication
from .reportsenderexception import ReportSenderException


class ReportSender:
    @staticmethod
    def send_report_email(report_file, to_email, eval_id):
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
        ReportSender.send_email(to_email, subject, body_text, body_html, report_file)

    @staticmethod
    def send_email(to_email, subject, body_text, body_html, report_file):
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
        att = MIMEApplication(open(report_file, 'rb').read())
        att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(report_file))
        msg.attach(msg_body)
        msg.attach(att)
        try:
            client.send_raw_email(
                Source=sender,
                Destinations=[to_email],
                RawMessage={'Data': msg.as_string()},
            )
        except ClientError:
            raise ReportSenderException()
