from decimal import Decimal
from typing import Any, Dict

from app.payment.models.payment import PaymentMethod, PaymentStatus, PaymentType
from app.payment.services.payment_config import PaymentSettings
from common.exceptions.payment_exception import PaymentValidationError


class PaymentValidator:
    def __init__(self) -> None:
        self.config: PaymentSettings = PaymentSettings()

    async def validate_payment_data(self, payment_data: Dict[str, Any]) -> None:
        """결제 데이터 기본 검증"""
        try:
            # 필수 필드 검증
            required_fields = ["amount", "payment_method", "payment_type", "name"]
            for field in required_fields:
                if not payment_data.get(field):
                    raise PaymentValidationError(f"{field}가 누락되었습니다")

            # 금액 검증
            amount = payment_data.get("amount")
            if not isinstance(amount, (int, float, Decimal)):
                raise PaymentValidationError("결제 금액이 유효하지 않습니다")

            if Decimal(str(amount)) <= 0:
                raise PaymentValidationError("결제 금액은 0보다 커야 합니다")

            if Decimal(str(amount)) > self.config.PAYMENT_CONFIG["MAX_AMOUNT"]:
                raise PaymentValidationError("최대 결제 금액을 초과했습니다")

            # 결제 수단 검증
            payment_method = payment_data.get("payment_method")
            if payment_method not in PaymentMethod.__members__.values():
                raise PaymentValidationError("유효하지 않은 결제 수단입니다")

            # PG사 검증
            payment_type = payment_data.get("payment_type")
            if payment_type not in PaymentType.__members__.values():
                raise PaymentValidationError("유효하지 않은 PG사입니다")

        except PaymentValidationError:
            raise
        except Exception as e:
            raise PaymentValidationError(f"결제 데이터 검증 중 오류가 발생했습니다: {str(e)}")

    @staticmethod
    async def validate_payment_status(current_status: PaymentStatus, next_status: PaymentStatus) -> None:
        """결제 상태 변경 검증"""
        try:
            valid_transitions = {
                PaymentStatus.READY: [PaymentStatus.RESERVED],
                PaymentStatus.RESERVED: [PaymentStatus.CHECKOUT],
                PaymentStatus.CHECKOUT: [PaymentStatus.PAID, PaymentStatus.FAILED],
                PaymentStatus.PAID: [PaymentStatus.CANCELLED],
                PaymentStatus.FAILED: [PaymentStatus.READY],
            }

            if next_status not in valid_transitions.get(current_status, []):
                raise PaymentValidationError(f"잘못된 결제 상태 변경: {current_status} -> {next_status}")

        except PaymentValidationError:
            raise
        except Exception as e:
            raise PaymentValidationError(f"결제 상태 검증 중 오류가 발생했습니다: {str(e)}")
