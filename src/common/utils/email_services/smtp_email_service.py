from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from common.utils.email_services.email_service import EmailService
from core.configs import settings


class SmtpEmailService(EmailService):
    def __init__(self) -> None:
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.SMTP_USER,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
        )
        self.fm = FastMail(self.conf)

    async def send_email(self, to: str, subject: str, message: str) -> dict[str, str]:
        message_obj = MessageSchema(
            subject=subject,  # 이메일 제목
            recipients=[to],  # 수신자 이메일 리스트
            body=message,  # 이메일 본문
            subtype="html",  # 이메일 본문 형식 (HTML)
        )

        try:
            await self.fm.send_message(message_obj)
            return {"status": "success", "message": "Email sent successfully."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
