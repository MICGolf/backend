import hashlib
import hmac
import json
from datetime import datetime
from typing import Any, Dict, Union, cast

from app.payment.models.payment import NonUserPayment, PaymentStatus, UserPayment
from app.payment.services.payment_config import PaymentSettings
from app.payment.services.portone_service import PortoneService
from common.exceptions.payment_exception import PaymentNotFoundError, PaymentValidationError


class WebhookService:
    def __init__(self) -> None:
        self.portone_service: PortoneService = PortoneService()
        self.config: PaymentSettings = PaymentSettings()

    async def _verify_webhook_signature(self, webhook_data: Dict[str, Any], signature: str) -> bool:
        """웹훅 시그니처 검증"""
        try:
            if not self.config.WEBHOOK_SECRET:
                raise PaymentValidationError("웹훅 시크릿이 설정되지 않았습니다")

            # 데이터를 정렬된 JSON 문자열로 변환
            message = json.dumps(webhook_data, sort_keys=True)

            # HMAC-SHA256 서명 생성
            hmac_obj = hmac.new(
                self.config.WEBHOOK_SECRET.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256,
            )
            calculated_signature = hmac_obj.hexdigest()

            # 시그니처 비교
            return hmac.compare_digest(calculated_signature, signature)
        except Exception as e:
            raise PaymentValidationError(f"웹훅 시그니처 검증 실패: {str(e)}")

    async def handle_payment_webhook(self, webhook_data: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """포트원 결제 웹훅 처리"""
        try:
            merchant_uid = webhook_data.get("merchant_uid")
            imp_uid = webhook_data.get("imp_uid")
            status = webhook_data.get("status")

            # 결제 정보 조회
            payment: Union[UserPayment, NonUserPayment, None] = await UserPayment.get_or_none(merchant_uid=merchant_uid)
            if payment is None:
                payment = await NonUserPayment.get_or_none(merchant_uid=merchant_uid)
            if payment is None:
                raise PaymentNotFoundError("결제 정보를 찾을 수 없습니다")

            # 웹훅 시그니처 검증
            if not await self._verify_webhook_signature(webhook_data, signature):
                raise PaymentValidationError("유효하지 않은 웹훅 요청입니다")

            # 결제 상태 업데이트
            if status == PaymentStatus.PAID:
                payment.paid_at = cast(datetime, webhook_data.get("paid_at"))
            elif status == PaymentStatus.FAILED:
                payment.failed_at = cast(datetime, webhook_data.get("failed_at"))
                payment.fail_reason = cast(str, webhook_data.get("fail_reason"))
            elif status == PaymentStatus.CANCELLED:
                payment.cancelled_at = cast(datetime, webhook_data.get("cancelled_at"))

            payment.status = cast(PaymentStatus, status)
            payment.imp_uid = cast(str, imp_uid)
            await payment.save()

            return {
                "status": "success",
                "message": f"Webhook processed for payment {merchant_uid}",
                "payment_status": payment.status,
            }

        except Exception as e:
            raise PaymentValidationError(f"웹훅 처리 실패: {str(e)}")
