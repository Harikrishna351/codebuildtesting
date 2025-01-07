import smtplib
from email.mime.text import MIMEText

def send_email(message):
    smtp_server = "email-smtp.us-east-1.amazonaws.com"
    smtp_port = 587
    smtp_username = "AKIAS74TLYHELKOX7D74"
    smtp_password = "BOnvUFr8KQHsryZa3a/r2NRXSASK6UbhSpRIwLamvEZD"
    from_email = "harikarn10@gmail.com"
    to_email = "harikrishnatangelapally@gmail.com"

    msg = MIMEText(message)
    msg['Subject'] = 'AWS CodeBuild Notification'
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())

if __name__ == "__main__":
    import sys
    send_email(sys.argv[1])
