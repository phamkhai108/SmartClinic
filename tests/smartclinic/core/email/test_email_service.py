import datetime
import smtplib

import pytest

from smartclinic.core.email.email_service import send_verification_email


class FakeSMTPSuccess:
    def __init__(self, *args, **kwargs):
        pass

    def starttls(self):
        pass

    def login(self, sender_email, password):
        pass

    def sendmail(self, sender_email, receiver_email, text):
        # Check that the text contains the verification code and the current year
        assert str(datetime.datetime.now().year) in text

    def quit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FakeSMTPFailure:
    def __init__(self, *args, **kwargs):
        pass

    def starttls(self):
        pass

    def login(self, sender_email, password):
        pass

    def sendmail(self, sender_email, receiver_email, text):
        raise smtplib.SMTPException("Simulated email send failure")

    def quit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def test_send_verification_email_success(monkeypatch: pytest.MonkeyPatch):
    # Monkey-patch smtplib.SMTP to always succeed
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTPSuccess)
    receiver_email = "test@example.com"
    success, code = send_verification_email(receiver_email)

    # Check that the function indicate success and returns a 6-digit verification code
    assert success is True
    assert isinstance(code, str)
    assert len(code) == 6
    assert code.isdigit()


def test_send_verification_email_failure(monkeypatch: pytest.MonkeyPatch):
    # Monkey-patch smtplib.SMTP to simulate a failure during sending
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTPFailure)
    receiver_email = "test@example.com"
    success, error = send_verification_email(receiver_email)

    # Check that the function returns failure and an appropriate error message
    assert success is False
    assert "Simulated email send failure" in error