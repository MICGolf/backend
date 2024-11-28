# dtos/order_request.py
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, conlist


class OrderProductRequest(BaseModel):
    product_id: int = Field(..., description="상품 ID")
    quantity: int = Field(..., gt=0, description="주문 수량")
    price: Decimal = Field(..., gt=0, description="상품 가격")


class CreateOrderRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="주문자 이름")
    phone: str = Field(..., min_length=10, max_length=20, description="연락처")
    email: Optional[EmailStr] = Field(None, description="이메일")
    shipping_address: str = Field(..., min_length=1, max_length=255, description="배송지 주소")
    detail_address: Optional[str] = Field(None, max_length=255, description="상세 주소")
    request: Optional[str] = Field(None, description="배송 요청사항")
    products: List[OrderProductRequest] = Field(..., min_items=1, description="주문 상품 목록")  # type: ignore


class OrderVerificationRequest(BaseModel):
    order_number: str = Field(..., description="주문번호")
    phone: str = Field(..., description="주문자 전화번호")


class PaymentRequest(BaseModel):
    order_id: int = Field(..., description="주문 ID")
    imp_uid: str = Field(..., description="포트원 결제 번호")
    merchant_uid: str = Field(..., description="주문번호")
    amount: Decimal = Field(..., gt=0, description="결제 금액")
    payment_type: str = Field(..., description="결제 방식")


class RefundRequest(BaseModel):
    order_id: int = Field(..., description="주문 ID")
    reason: str = Field(..., min_length=1, description="환불 사유")
    refund_amount: Decimal = Field(..., gt=0, description="환불 금액")


class UpdateShippingRequest(BaseModel):
    courier: str = Field(..., description="배송사")
    tracking_number: str = Field(..., description="운송장 번호")
    shipping_status: str = Field(..., description="배송 상태")
