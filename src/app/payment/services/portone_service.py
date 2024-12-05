from typing import Any, Dict, Optional, TypedDict

import httpx

from app.payment.services.payment_config import PaymentSettings
from common.exceptions.payment_exception import PaymentProcessError


class PortoneResponse(TypedDict):
    code: int
    message: str
    response: Dict[str, Any]


class PortoneService:
    def __init__(self) -> None:
        self.config: PaymentSettings = PaymentSettings()
        self.base_url: str = self.config.PORTONE_BASE_URL
        self.access_token: Optional[str] = None
        self.timeout = httpx.Timeout(30.0)

    async def _get_access_token(self) -> str:
        """포트원 액세스 토큰 발급"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/users/getToken",
                    json={
                        "imp_key": self.config.PORTONE_API_KEY,
                        "imp_secret": self.config.PORTONE_API_SECRET,
                    },
                )
                result: PortoneResponse = response.json()
                if result.get("code") == 0:
                    return str(result["response"]["access_token"])
                raise PaymentProcessError("액세스 토큰 발급 실패")
        except Exception as e:
            raise PaymentProcessError(f"포트원 API 호출 실패: {str(e)}")

    async def reserve_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: 결제 예약"""
        try:
            if not self.access_token:
                self.access_token = await self._get_access_token()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/payments/prepare",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=payment_data,
                )
                result: PortoneResponse = response.json()
                if result.get("code") == 0:
                    return dict(result["response"])
                raise PaymentProcessError("결제 예약 실패")
        except Exception as e:
            raise PaymentProcessError(f"결제 예약 실패: {str(e)}")

    async def checkout_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: 결제 요청"""
        try:
            if not self.access_token:
                self.access_token = await self._get_access_token()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/subscribe/payments/onetime",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=payment_data,
                )
                result: PortoneResponse = response.json()
                if result.get("code") == 0:
                    return dict(result["response"])
                raise PaymentProcessError("결제 요청 실패")
        except Exception as e:
            raise PaymentProcessError(f"결제 요청 실패: {str(e)}")

    async def approve_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: 결제 승인"""
        try:
            if not self.access_token:
                self.access_token = await self._get_access_token()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/payments/{payment_data['imp_uid']}/approve",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=payment_data,
                )
                result: PortoneResponse = response.json()
                if result.get("code") == 0:
                    return dict(result["response"])
                raise PaymentProcessError("결제 승인 실패")
        except Exception as e:
            raise PaymentProcessError(f"결제 승인 실패: {str(e)}")
