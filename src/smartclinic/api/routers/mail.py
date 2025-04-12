from fastapi import APIRouter
from pydantic import BaseModel

from smartclinic.core.mailer.emaiil_dto import EmailResponse
from smartclinic.core.mailer.email_controller import handel_mail

router = APIRouter(prefix="/send_mail", tags=["Mail"])


class EmailRequest(BaseModel):
    receiver_email: str


@router.post(
    "",
    summary="Send email",
    description="Send a verification code to the user's email",
)
def send_mail(email_request: EmailRequest) -> EmailResponse:
    email_response = handel_mail(email_request.receiver_email)
    return email_response
