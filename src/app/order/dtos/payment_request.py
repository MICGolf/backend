from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.order.models.payment import PaymentType


class PaymentBaseRequestDTO(BaseModel):
    """결제 요청 기본 DTO"""

    amount: Decimal = Field(..., description="결제 금액", examples=[Decimal("10000.00")], gt=0)
    payment_type: Optional[PaymentType] = Field(default=PaymentType.KAKAO_PAY, description="PG사")


class PaymentReserveRequestDTO(PaymentBaseRequestDTO):
    """결제 예약 요청 DTO"""

    user_id: Optional[int] = Field(None, description="회원 ID (회원 결제시)")
    user_order_id: Optional[int] = Field(None, description="회원 주문 ID (회원 결제시)")
    non_user_order_id: Optional[int] = Field(None, description="비회원 주문 ID (비회원 결제시)")


class PaymentApproveRequestDTO(BaseModel):
    """결제 승인 요청 DTO"""

    payment_id: str = Field(..., description="가맹점 거래 고유번호")
    tx_id: str = Field(..., description="포트원 거래 고유번호")
