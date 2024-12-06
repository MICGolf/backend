from typing import Any, Dict

from pydantic_settings import BaseSettings


class PaymentSettings(BaseSettings):
    """결제 설정"""

    # 포트원 API 설정
    PORTONE_API_KEY: str = "your_api_key"
    PORTONE_API_SECRET: str = "your_api_secret"
    PORTONE_BASE_URL: str = "https://api.iamport.kr"

    # PG사별 상점 ID 설정
    NICE_MERCHANT_ID: str = ""
    INICIS_MERCHANT_ID: str = ""
    TOSS_MERCHANT_ID: str = ""
    KAKAO_MERCHANT_ID: str = ""

    # 테스트/운영 환경 설정
    SANDBOX: bool = True  # True: 테스트, False: 운영

    # 결제 설정
    PAYMENT_CONFIG: Dict[str, Any] = {
        "MIN_AMOUNT": 100,  # 최소 결제 금액
        "MAX_AMOUNT": 10000000,  # 최대 결제 금액
        "DEFAULT_PG": "nice",  # 기본 PG사
        "ALLOWED_METHODS": [
            "card",
            "trans",
            "vbank",
            "phone",
            "kakaopay",
            "naverpay",
            "payco",
            "tosspay",
        ],
        "TOKEN_EXPIRE_MINUTES": 30,  # 토큰 만료 시간(분)
    }

    # 웹훅 설정
    WEBHOOK_SECRET: str
    WEBHOOK_URLS: Dict[str, str] = {
        "payment": "/api/v1/payments/webhook",
        "billing": "/api/v1/billings/webhook",
    }

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def get_pg_config(self) -> Dict[str, Any]:
        """PG사 설정 반환"""
        return {
            "nice": {
                "merchant_id": self.NICE_MERCHANT_ID,
                "enabled": True,
                "sandbox": self.SANDBOX,
            },
            "inicis": {
                "merchant_id": self.INICIS_MERCHANT_ID,
                "enabled": True,
                "sandbox": self.SANDBOX,
            },
            "tosspayments": {
                "merchant_id": self.TOSS_MERCHANT_ID,
                "enabled": True,
                "sandbox": self.SANDBOX,
            },
            "kakaopay": {
                "merchant_id": self.KAKAO_MERCHANT_ID,
                "enabled": True,
                "sandbox": self.SANDBOX,
            },
        }
