from abc import ABC, abstractmethod


class EmailService(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, message: str) -> dict[str, str]:
        pass
