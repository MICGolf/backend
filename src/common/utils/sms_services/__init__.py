from common.utils.sms_services.sms_service import SmsService
from core.configs import settings


def get_sms_service() -> "SmsService":
    from common.utils.sms_services.ncp_sms_service import NcpSmsService

    service_type = settings.SMS_SERVICE_TYPE
    if service_type == "ncp":
        return NcpSmsService()
    else:
        raise ValueError(f"Unsupported SMS service type: {service_type}")
