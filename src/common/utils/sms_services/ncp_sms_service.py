import httpx

from common.utils.sms_services.sms_service import SmsService
from core.configs import settings


class NcpSmsService(SmsService):
    def __init__(self) -> None:
        self.api_key = settings.NCP_API_KEY
        self.api_secret = settings.NCP_API_SECRET
        self.from_number = settings.NCP_SMS_FROM_NUMBER

    async def send_sms(self, phone_number: str, message: str) -> dict[str, str]:
        url = "https://api.ncloud-docs.com/sms/v1.0/send"
        headers = {
            "Content-Type": "application/json",
            "X-NCP-APIGW-API-KEY-ID": self.api_key,
            "X-NCP-APIGW-API-KEY": self.api_secret,
        }

        data = {
            "type": "SMS",
            "countryCode": "82",
            "from": self.from_number,  # 발신 번호
            "to": phone_number,
            "content": message,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return {"status": "success", "message": "SMS sent successfully."}
        else:
            return {"status": "error", "message": response.text}
