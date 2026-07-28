from __future__ import annotations

from smartclinic.core.mailer import EmailResponseDTO, EmailService


def handle_mail(mailer: EmailService, receiver_email: str) -> EmailResponseDTO:
    return mailer.send_verification_email(receiver_email)
