from abc import ABC, abstractmethod


class SmsService(ABC):
    @abstractmethod
    async def send_sms(self, phone_number: str, message: str) -> dict[str, str]:
        pass
