import datetime
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_verification_email(receiver_email):
    so_co_6_chu_so = f"{random.randint(000000, 999999):06d}"

    # Thông tin người gửi
    sender_email = "email@gmail.com"
    password = "password"  # Đảm bảo sử dụng mật khẩu an toàn

    # Tạo một đối tượng MIMEMultipart
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"SmartClinic: Your Verification Code {so_co_6_chu_so}"

    # Nội dung email định dạng HTML
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
            <p>Mã xác minh của bạn là <strong>{so_co_6_chu_so}</strong>. Vui lòng sử dụng mã này để hoàn tất việc đăng ký tài khoản tại <a href="https://www.smartclinic.com" target="_blank"><strong>SmartClinic</strong></a>. Mã này chỉ có hiệu lực trong vòng 5 phút.</p>
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

    # Gửi email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as session:
            session.starttls()
            session.login(sender_email, password)
            text = message.as_string()
            session.sendmail(sender_email, receiver_email, text)
        return True, so_co_6_chu_so  # Trả về mã xác minh
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False, str(e)


send_verification_email("kikipham1008@gmail.com")
