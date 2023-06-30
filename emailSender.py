import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os,time

class EmailSender():

    def __init__(self, smtp_server, smtp_port, smtp_username, smtp_password) -> None:
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    def sendHtml(self, to, title, context):

        message = MIMEMultipart()
        message["From"] = self.smtp_username
        message["To"] = to
        message["Subject"] = title

        html_part = MIMEText(context, "html")
        message.attach(html_part)

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.smtp_username, to, message.as_string())
        except smtplib.SMTPException as e:
            print("email send failed:", str(e))
