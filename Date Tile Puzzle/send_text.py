import smtplib
from email.mime.multipart import MIMEMultipart

class Texter:
    email = "redacted"
    passwd = "redacted"
    gateway = "redacted"
    smtp = "smtp.gmail.com"
    port = 587

    def __enter__(self):
        self.server = smtplib.SMTP(Texter.smtp, Texter.port)
        self.server.starttls()
        self.server.login(Texter.email, Texter.passwd)
        return self

    def send(self, body):
        msg = MIMEMultipart()
        msg["From"] = Texter.email
        msg["To"] = Texter.gateway
        msg["Subject"] = "\n"
        body += "\n"

        self.server.sendmail(Texter.email, Texter.gateway, body)

    def __exit__(self, *args):
        self.server.quit()
