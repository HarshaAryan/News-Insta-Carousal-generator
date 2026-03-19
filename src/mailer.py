import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECEIVER, get_logger

logger = get_logger("Mailer")

class Mailer:
    def __init__(self):
        if not EMAIL_USER or not EMAIL_PASSWORD:
            logger.warning("Email credentials missing. Mailer disabled.")
            self.disabled = True
        else:
            self.disabled = False
            self.user = EMAIL_USER
            self.password = EMAIL_PASSWORD
            self.receiver = EMAIL_RECEIVER or EMAIL_USER

    def send_email(self, subject, body, attachments=None):
        if self.disabled:
            logger.info(f"Mock Email Sent: {subject}")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = self.receiver
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            if attachments:
                for fpath in attachments:
                    path = Path(fpath)
                    if path.exists():
                        with open(path, "rb") as f:
                            part = MIMEApplication(f.read(), Name=path.name)
                            part['Content-Disposition'] = f'attachment; filename="{path.name}"'
                            msg.attach(part)
                    else:
                        logger.warning(f"Attachment not found: {fpath}")

            # Send via Gmail SMTP
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {self.receiver}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    m = Mailer()
    m.send_email("Test Subject", "Test Body")
