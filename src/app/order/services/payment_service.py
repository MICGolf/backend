import asyncio
import time
import uuid
from typing import Any, Optional, Type

from app.order.dtos.payment_request import PaymentApproveRequestDTO, PaymentReserveRequestDTO
from app.order.dtos.payment_response import PaymentReserveResponseDTO
from app.order.models.order import NonUserOrder, NonUserOrderProduct
from app.order.models.payment import NonUserPayment, PaymentStatus


class MerchantUIDGenerator:
    @staticmethod
    async def _create_merchant_uid_generator(prefix: str = "") -> str:
        timestamp: int = int(time.time())
        unique_id: str = uuid.uuid4().hex[:8]
        return f"{prefix}_{timestamp}_{unique_id}"


class PaymentService:
    def __init__(self) -> None:
        self._merchant_uid_generator: MerchantUIDGenerator = MerchantUIDGenerator()

    async def reserve_payment(self, payment_data: PaymentReserveRequestDTO) -> PaymentReserveResponseDTO:
        """
        결제 예약
        """
        merchant_uid: str = await self._merchant_uid_generator._create_merchant_uid_generator(prefix="PAYMENT")

        payment_model = await self.get_payment_model(payment_data.user_id)

        order = await NonUserOrder.get(id=payment_data.non_user_order_id)

        payment = await payment_model.create(
            transaction_id=merchant_uid,
            amount=payment_data.amount,
            payment_type=payment_data.payment_type,
            payment_status=PaymentStatus.RESERVED.value,
            order=order,
        )
        await payment.save()

        return await PaymentReserveResponseDTO.build(payment_id=payment.transaction_id)

    @staticmethod
    async def get_payment_model(user_id: Optional[int]) -> Type[NonUserPayment]:
        return NonUserPayment

    @staticmethod
    async def approve_payment(payment_data: PaymentApproveRequestDTO) -> None:
        """
        결제 승인
        """
        payment = await NonUserPayment.get(transaction_id=payment_data.payment_id).prefetch_related(
            "order__order_product"
        )

        payment.payment_status = PaymentStatus.PAID.value
        payment.approval_number = payment_data.tx_id

        tasks = []

        if hasattr(payment.order, "order_product"):
            products = payment.order.order_product

            for product in products:
                product.current_status = "ITEM_PENDING"
                tasks.append(product.save())

        tasks.append(payment.save())
        await asyncio.gather(*tasks)
