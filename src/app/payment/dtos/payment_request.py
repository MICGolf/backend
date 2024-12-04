from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.payment.models.payment import PaymentMethod, PaymentType


class PaymentBaseRequestDTO(BaseModel):
    """결제 요청 기본 DTO"""

    amount: Decimal = Field(..., description="결제 금액")
    payment_method: PaymentMethod = Field(..., description="결제 수단")
    payment_type: PaymentType = Field(..., description="PG사")
    name: str = Field(..., description="상품명")
    buyer_name: Optional[str] = Field(None, description="구매자명")
    buyer_email: Optional[str] = Field(None, description="구매자 이메일")
    buyer_tel: Optional[str] = Field(None, description="구매자 연락처")
    notice_url: Optional[str] = Field(None, description="웹훅 URL")


class PaymentReserveRequestDTO(PaymentBaseRequestDTO):
    """결제 예약 요청 DTO"""

    user_id: Optional[int] = Field(None, description="회원 ID (회원 결제시)")
    non_user_order_id: Optional[int] = Field(None, description="비회원 주문 ID (비회원 결제시)")


class PaymentCheckoutRequestDTO(BaseModel):
    """결제 요청 DTO"""

    merchant_uid: str = Field(..., description="가맹점 거래 고유번호")
    card_number: str = Field(..., description="카드번호")
    expiry: str = Field(..., description="카드 유효기간(YYYY-MM)")
    birth: str = Field(..., description="생년월일6자리")
    pwd_2digit: Optional[str] = Field(None, description="카드 비밀번호 앞 2자리")


class PaymentApproveRequestDTO(BaseModel):
    """결제 승인 요청 DTO"""

    merchant_uid: str = Field(..., description="가맹점 거래 고유번호")
    imp_uid: str = Field(..., description="포트원 거래 고유번호")
