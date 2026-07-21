from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from smartclinic.api.dependencies import get_mailer_service
from smartclinic.api.deps_auth import CurrentUser, require_roles
from smartclinic.core.mailer.emaiil_dto import EmailRequestDTO, EmailResponseDTO
from smartclinic.core.mailer.email_controller import handel_mail
from smartclinic.core.mailer.email_service import EmailService

router = APIRouter(prefix="/send_mail", tags=["Mail"])


@router.post("")
def send_mail(
    email_request: EmailRequestDTO,
    _admin: Annotated[CurrentUser, Depends(require_roles("admin"))],
    mail_client: Annotated[EmailService, Depends(get_mailer_service)],
) -> EmailResponseDTO:
    email_response = handel_mail(mail_client, email_request.receiver_email)
    if not email_response.code_verify:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "FEATURE_UNAVAILABLE",
                "message": "Failed to send verification email.",
                "keys": [],
            },
        )
    return EmailResponseDTO(
        email=email_response.email,
        code_verify=None,
        received_time=email_response.received_time,
    )
