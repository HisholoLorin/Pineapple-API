#appPassword = aavuugaclliuttwu
from email.message import EmailMessage
import ssl
import smtplib
from core.config import getSetting

def sendEmail(username, emailReciver, otp):
    emailSender = getSetting().EMAIL_SENDER
    emailPassword = getSetting().EMAIL_PASSWORD

    subject = "Pineapple Forget Password OTP"
    body = f"Hi {username},\n\nYour otp is {otp}.\n\nRegards,\n@Pineapple"

    em = EmailMessage()
    em['From'] = emailSender
    em['To'] = emailReciver
    em['subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com',465, context=context) as smtp:
        smtp.login(emailSender, emailPassword)
        smtp.sendmail(emailSender,emailReciver, em.as_string())