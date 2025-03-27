from smartclinic.common import AppConfig
from smartclinic.core.mailer import EmailResponse, EmailService


def handel_mail(receiver_email: str) -> EmailResponse:
    mailer = EmailService(AppConfig.sender_email, AppConfig.sender_password)
    email_response = mailer.send_verification_email(receiver_email)
    return email_response
