from __future__ import annotations

import smtplib
from unittest.mock import MagicMock

from smartclinic.core.mailer.email_service import EmailService


def test_send_verification_email_success(monkeypatch):
    smtp = MagicMock()
    smtp.__enter__.return_value = smtp
    smtp.__exit__.return_value = False
    monkeypatch.setattr(
        "smartclinic.core.mailer.email_service.smtplib.SMTP",
        lambda *_a, **_k: smtp,
    )
    monkeypatch.setattr(
        "smartclinic.core.mailer.email_service.random.randint",
        lambda _a, _b: 42,
    )

    service = EmailService("sender@example.com", "pw")
    response = service.send_verification_email("recv@example.com")

    assert response.email == "recv@example.com"
    assert response.code_verify == "000042"
    assert response.received_time is not None
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once_with("sender@example.com", "pw")
    smtp.sendmail.assert_called_once()
    assert smtp.sendmail.call_args.kwargs["to_addrs"] == "recv@example.com"


def test_send_verification_email_smtp_failure(monkeypatch):
    class BoomSMTP:
        def __init__(self, *_a, **_k):
            pass

        def __enter__(self):
            raise smtplib.SMTPException("down")

        def __exit__(self, *_a):
            return False

    monkeypatch.setattr(
        "smartclinic.core.mailer.email_service.smtplib.SMTP",
        BoomSMTP,
    )
    service = EmailService("sender@example.com", "pw")
    response = service.send_verification_email("recv@example.com")
    assert response.email is None
    assert response.code_verify is None
    assert response.received_time is not None
