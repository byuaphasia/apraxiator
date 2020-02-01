import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class WaiverSender:
    def __init__(self):
        auth_dir = '../apx-resources/email/'
        creds_json = open(os.path.join(auth_dir, 'creds.json'))
        creds = json.load(creds_json)
        self.email = creds['email']
        self.username = creds['username']
        self.password = creds['password']

    def send_waiver(self, waiver_file, to_email):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to_email
        msg['Subject'] = "Signed copy of HIPAA Waiver"
        body = "Attached below is your signed copy of the HIPAA Waiver"
        msg.attach(MIMEText(body, 'plain'))
        filename = "Signed HIPAA Waiver.pdf"
        attachment = open(waiver_file, "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload(attachment.read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(self.email, self.password)
        text = msg.as_string()
        s.sendmail(self.email, to_email, text)
        s.quit()
