from fastapi import APIRouter, Depends

from smartclinic.common import AppConfig
from smartclinic.core.mailer.emaiil_dto import EmailRequestDTO, EmailResponseDTO
from smartclinic.core.mailer.email_controller import handel_mail
from smartclinic.core.mailer.email_service import EmailService

router = APIRouter(prefix="/send_mail", tags=["Mail"])


def mail_client() -> EmailService:
    return EmailService(
        sender_email=AppConfig.sender_email,
        sender_password=AppConfig.sender_password,
    )


@router.post(
    "",
    summary="Send email",
    description="Send a verification code to the user's email",
)
def send_mail(
    email_request: EmailRequestDTO,
    mail_client=Depends(mail_client),  # noqa: B008
) -> EmailResponseDTO:
    email_response = handel_mail(mail_client, email_request.receiver_email)
    return email_response
