import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path

emailID = 'user2146@vwb.me'
password = 's6J#D*R6OQqDz'

def send_email(recipient, email_subject, message):
    msg = MIMEMultipart()
    msg['From'] = emailID  # sender
    msg['To'] = recipient
    msg['Subject'] = email_subject
    msg.attach(MIMEText(message, 'plain'))
    #
    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.ehlo()
        server.starttls()
        server.login(emailID, password)
        text = msg.as_string()
        server.sendmail(emailID, recipient, text)
        print('email sent')
        server.quit()
    except:
        print("SMPT server connection error")
    return True

if __name__ == '__main__':
    send_email('pkqrgqxsjfwws@affecting.org', 'Happy New Year', 'We love Outlook')
