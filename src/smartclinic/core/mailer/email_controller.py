from smartclinic.core.mailer import EmailResponseDTO, EmailService


def handel_mail(mailer: EmailService, receiver_email: str) -> EmailResponseDTO:
    email_response = mailer.send_verification_email(receiver_email)
    return email_response
