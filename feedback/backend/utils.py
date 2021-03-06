from . import app

import smtplib
import string
import random

from email.mime.text import MIMEText
from email.utils import formatdate


def generate_passwd(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def send_mail(address, passwd):
    """
    Send verification emails based on below template.
    """
    message = (
        "Hey there!\n\nYour HOBY Feedback account is ready to be logged "
        + "into. If you have any problems logging in, please contact the "
        + "operations staff who created your account."
        + "\n\nURL: https://feedback.hobynye.org\nPassword: {}\n\n"
        + "Please change this password once you have logged in.\n\n"
        + "Thanks,\nHOBY NYE\n"
        + "\n\nThis message was automatically generated by HOBY Feedback"
    )

    message = message.format(passwd)

    email = MIMEText(message)
    email["To"] = address
    email["From"] = "HOBY Feedback <{}>".format(app.config["EMAIL_USER"])
    email["Subject"] = "Your HOBY Feedback Account"
    email["Date"] = formatdate()

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(app.config["EMAIL_USER"], app.config["EMAIL_PASS"])
    server.send_message(email)
    server.quit()
