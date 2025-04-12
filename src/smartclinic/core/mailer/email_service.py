import datetime
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from smartclinic.core.mailer.emaiil_dto import EmailResponseDTO


class EmailService:
    def __init__(self, sender_email: str, sender_password: str) -> None:
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_verification_email(self, receiver_email: str) -> EmailResponseDTO:
        code_verify = f"{random.randint(000000, 999999):06d}"

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = receiver_email
        message["Subject"] = f"SmartClinic: Your Verification Code {code_verify}"

        # Email content in HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f9f9f9;
                    color: #333;
                    line-height: 1.6;
                    padding: 20px;
                }}
                h1 {{
                    color: #007bff;
                    font-size: 24px;
                }}
                .container {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #777;
                }}
                a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>Xin chào,</p>
                <p>Mã xác minh của bạn là <strong>{code_verify}</strong>. Vui lòng sử dụng mã này để hoàn tất việc đăng ký tài khoản tại <a href="https://www.smartclinic.com" target="_blank"><strong>SmartClinic</strong></a>. Mã này chỉ có hiệu lực trong vòng 5 phút.</p>
                <p>Xin lưu ý: Tuyệt đối không chia sẻ mã này với bất kỳ ai. Nếu bạn không yêu cầu xác minh email tại SmartClinic, xin vui lòng bỏ qua email này.</p>
                <p>Thân ái!</p>
                <a href="https://www.smartclinic.com"><h1>SmartClinic</h1></a>
            </div>
            <div class="footer">
                <p>&copy; {datetime.datetime.now().year} SmartClinic. All rights reserved.</p>
            </div>
        </body>
        </html>
        """  # noqa: E501

        # Tạo một phần MIME có chứa nội dung HTML
        part1 = MIMEText(html, "html")
        message.attach(part1)

        # send email
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as session:
                session.starttls()
                session.login(self.sender_email, self.sender_password)
                content_msg = message.as_string()
                session.sendmail(
                    from_addr=self.sender_email,
                    to_addrs=receiver_email,
                    msg=content_msg,
                )

            code_verify = EmailResponseDTO(
                email=receiver_email,
                code_verify=code_verify,
                received_time=datetime.datetime.now(),
            )
            return code_verify

        except smtplib.SMTPException:
            return EmailResponseDTO(
                email=None,
                code_verify=None,
                received_time=datetime.datetime.utcnow(),
            )
