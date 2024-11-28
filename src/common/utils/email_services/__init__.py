from common.utils.email_services.email_service import EmailService
from core.configs import settings


def get_email_service() -> "EmailService":
    from common.utils.email_services.smtp_email_service import SmtpEmailService

    service_type = settings.EMAIL_SERVICE_TYPE
    if service_type == "smtp":
        return SmtpEmailService()
    else:
        raise ValueError(f"Unsupported email service type: {service_type}")
