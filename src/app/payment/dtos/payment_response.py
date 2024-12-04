from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PaymentBaseResponseDTO(BaseModel):
    """결제 응답 기본 DTO"""

    merchant_uid: str = Field(..., description="가맹점 거래 고유번호")
    imp_uid: Optional[str] = Field(None, description="포트원 거래 고유번호")
    status: str = Field(..., description="결제 상태")
    amount: Decimal = Field(..., description="결제 금액")
    payment_method: str = Field(..., description="결제 수단")
    payment_type: str = Field(..., description="PG사")
    paid_at: Optional[str] = Field(None, description="결제 완료 시각")
    failed_at: Optional[str] = Field(None, description="결제 실패 시각")
    fail_reason: Optional[str] = Field(None, description="실패 사유")


class PaymentReserveResponseDTO(PaymentBaseResponseDTO):
    """결제 예약 응답 DTO"""

    reserved_at: str = Field(..., description="예약 시각")


class PaymentCheckoutResponseDTO(PaymentBaseResponseDTO):
    """결제 요청 응답 DTO"""

    checkout_url: str = Field(..., description="결제 요청 URL")


class PaymentApproveResponseDTO(PaymentBaseResponseDTO):
    """결제 승인 응답 DTO"""

    receipt_url: Optional[str] = Field(None, description="영수증 URL")
    card_info: Optional[Dict[str, Any]] = Field(None, description="카드 정보")
