from fastapi import APIRouter

from smartclinic.core.mailer.emaiil_dto import EmailResponse
from smartclinic.core.mailer.email_controller import handel_mail

router = APIRouter(prefix="/send_mail", tags=["Mail"])

@router.get(
    "",
    summary="Send email",
    description="Send a verification code to the user's email",
)
def send_mail(receiver_email: str) -> EmailResponse:
    email_response = handel_mail(receiver_email)
    return email_response   
