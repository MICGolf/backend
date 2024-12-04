import time
import uuid
from datetime import datetime
from typing import Any, Dict, Protocol, Union

from app.payment.models.payment import NonUserPayment, PaymentStatus, UserPayment
from app.payment.services.payment_validator import PaymentValidator
from app.payment.services.portone_service import PortoneService
from common.exceptions.payment_exception import PaymentNotFoundError, PaymentProcessError, PaymentValidationError


class MerchantUIDGenerator(Protocol):
    @staticmethod
    async def generate(prefix: str = "") -> str: ...


class PaymentService:
    def __init__(self) -> None:
        self.portone_service: PortoneService = PortoneService()
        self.validator: PaymentValidator = PaymentValidator()
        self._merchant_uid_generator: MerchantUIDGenerator = self._create_merchant_uid_generator()

    @staticmethod
    def _create_merchant_uid_generator() -> MerchantUIDGenerator:
        class DefaultMerchantUIDGenerator:
            @staticmethod
            async def generate(prefix: str = "") -> str:
                timestamp: int = int(time.time())
                unique_id: str = uuid.uuid4().hex[:8]
                return f"{prefix}_{timestamp}_{unique_id}"

        return DefaultMerchantUIDGenerator()

    async def _get_payment(self, merchant_uid: str) -> Union[UserPayment, NonUserPayment]:
        """결제 정보 조회 공통 메서드"""
        user_payment = await UserPayment.get_or_none(merchant_uid=merchant_uid)
        if user_payment:
            return user_payment

        non_user_payment = await NonUserPayment.get_or_none(merchant_uid=merchant_uid)
        if non_user_payment:
            return non_user_payment

        raise PaymentNotFoundError("결제 정보를 찾을 수 없습니다")

    async def reserve_payment(self, payment_data: Dict[str, Any], is_user: bool = False) -> Dict[str, Any]:
        """Step 1: 결제 예약"""
        try:
            await self.validator.validate_payment_data(payment_data)
            merchant_uid: str = await self._merchant_uid_generator.generate()
            payment_model = UserPayment if is_user else NonUserPayment

            payment = await payment_model.create(
                merchant_uid=merchant_uid,
                transaction_id=merchant_uid,
                amount=payment_data["amount"],
                payment_method=payment_data["payment_method"],
                payment_type=payment_data["payment_type"],
                user_id=payment_data.get("user_id") if is_user else None,
                status=PaymentStatus.RESERVED,
            )

            portone_response = await self.portone_service.reserve_payment(
                {
                    "merchant_uid": payment.merchant_uid,
                    "amount": payment.amount,
                    "payment_method": payment.payment_method,
                    "payment_type": payment.payment_type,
                    "name": payment_data["name"],
                }
            )

            if portone_response and isinstance(portone_response.get("pg_tid"), str):
                payment.pg_tid = portone_response["pg_tid"]
                await payment.save()

            return await payment.to_dict()

        except (PaymentValidationError, PaymentProcessError) as e:
            raise e
        except Exception as e:
            raise PaymentProcessError(f"알 수 없는 오류 발생: {str(e)}")

    async def checkout_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: 결제 요청"""
        try:
            payment = await self._get_payment(payment_data["merchant_uid"])
            await self.validator.validate_payment_status(payment.status, PaymentStatus.CHECKOUT)

            payment.status = PaymentStatus.CHECKOUT
            await payment.save()

            portone_response = await self.portone_service.checkout_payment(
                {
                    "merchant_uid": payment.merchant_uid,
                    "amount": payment.amount,
                    "card_number": payment_data["card_number"],
                    "expiry": payment_data["expiry"],
                    "birth": payment_data["birth"],
                    "pwd_2digit": payment_data.get("pwd_2digit"),
                }
            )

            if portone_response and isinstance(portone_response.get("pg_tid"), str):
                payment.pg_tid = portone_response["pg_tid"]
                await payment.save()

            return await payment.to_dict()

        except (PaymentValidationError, PaymentProcessError, PaymentNotFoundError) as e:
            raise e
        except Exception as e:
            raise PaymentProcessError(f"알 수 없는 오류 발생: {str(e)}")

    async def approve_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: 결제 승인"""
        try:
            payment = await self._get_payment(payment_data["merchant_uid"])
            await self.validator.validate_payment_status(payment.status, PaymentStatus.PAID)

            portone_response = await self.portone_service.approve_payment(
                {"merchant_uid": payment.merchant_uid, "imp_uid": payment_data["imp_uid"], "amount": payment.amount}
            )

            if portone_response:  # 응답 확인
                payment.status = PaymentStatus.PAID
                payment.imp_uid = payment_data["imp_uid"]
                payment.paid_at = datetime.now()
                await payment.save()

            return await payment.to_dict()

        except (PaymentValidationError, PaymentProcessError, PaymentNotFoundError) as e:
            raise e
        except Exception as e:
            raise PaymentProcessError(f"알 수 없는 오류 발생: {str(e)}")
