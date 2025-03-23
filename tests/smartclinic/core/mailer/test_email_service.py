import datetime

from pytest_mock import MockerFixture

from smartclinic.core.mailer import EmailResponselDto, EmailService


def test_send_verification_email(mocker: MockerFixture) -> None:
    mock_response = EmailResponselDto(
        email="dummy_email",
        code_verify="dummy_code",
        received_time=datetime.datetime.utcnow(),
    )

    email_service = EmailService("dummy_email@example.com", "dummy_password")
    mocker.patch.object(
        email_service,
        "send_verification_email",
        return_value=mock_response,
        autospec=True,
    )

    response = email_service.send_verification_email("dummy_email@example.com")

    assert response == mock_response
