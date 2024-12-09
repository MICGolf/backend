# dtos/order_request.py
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, EmailStr, Field, conlist


class PageType(str, Enum):
    UNPAID = "UNPAID"  # 결제 전 상태
    PROCUREMENT = "PENDING"  # 발주 관련 상태
    SHIPPING = "SHIPPING"  # 배송 관련 상태


class OrderProductRequest(BaseModel):
    product_id: int = Field(..., description="상품 ID")
    option_id: int = Field(..., description="옵션 ID")  # 옵션 ID 추가
    quantity: int = Field(..., gt=0, description="주문 수량")
    price: Decimal = Field(..., gt=0, description="상품 가격")


class CreateOrderRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="주문자 이름")
    phone: str = Field(..., min_length=10, max_length=20, description="연락처")
    shipping_address: str = Field(..., min_length=1, max_length=255, description="배송지 주소")
    detail_address: Optional[str] = Field(None, max_length=255, description="상세 주소")
    current_status: Optional[str] = "UNPAID"  # 기본값 추가
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
    order_id: int = Field(..., description="주문 ID")
    courier: str = Field(..., description="배송사")
    tracking_number: str = Field(..., description="운송장 번호")
    shipping_status: str = Field(..., description="배송 상태")


class OrderSearchRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    order_number: Optional[str] = None
    order_status: Optional[str] = None
    purchase_status: Optional[str] = None
    shipping_status: Optional[str] = None
    claim_status: Optional[str] = None
    sort_by: Optional[str] = None
    sort_direction: Optional[str] = Query("desc")
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    payment_status: Optional[str] = None


class BatchOrderStatusRequest(BaseModel):
    order_ids: List[int]
    status: str


class PurchaseOrderRequest(BaseModel):
    order_id: int = Field(..., description="주문 ID")
    status: str = Field("CONFIRMED", description="발주 상태")


class UpdateOrderStatusRequest(BaseModel):
    order_id: int = Field(..., description="주문 ID")
    status: str = Field(..., description="변경할 상태")


# dtos/order_request.py
class OrderClaimRequest(BaseModel):
    order_id: int = Field(..., description="주문 ID")
    claim_type: str = Field(..., description="클레임 유형 (RETURN/EXCHANGE/CANCEL)")
    claim_reason: str = Field(..., description="클레임 사유")
    claim_status: str = Field(..., description="클레임 상태")


class UpdatePurchaseStatusRequest(BaseModel):
    order_id: int = Field(..., description="주문 ID")
    purchase_status: str = Field(..., description="발주 상태 (CONFIRMED/CANCELED)")
    memo: Optional[str] = None


# order_request.py
class BatchUpdatePurchaseStatusRequest(BaseModel):
    order_ids: List[int] = Field(..., description="주문 ID 목록")
    purchase_status: str = Field(..., description="발주 상태")


# order_request.py에 추가
class UpdateOrderRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="주문자 이름")
    phone: str = Field(..., min_length=10, max_length=20, description="연락처")
    shipping_address: str = Field(..., min_length=1, max_length=255, description="배송지 주소")
    detail_address: Optional[str] = Field(None, max_length=255, description="상세 주소")
    request: Optional[str] = Field(None, description="배송 요청사항")


class SellerCancelRequest(BaseModel):
    order_id: int = Field(..., description="주문 ID")
    cancel_reason: str = Field(..., description="취소 사유")


class BatchUpdateShippingStatusRequest(BaseModel):
    order_ids: List[int] = Field(..., description="주문 ID 목록")
    shipping_status: str = Field(..., description="배송 상태")


class BulkUpdateShippingRequest(BaseModel):
    order_products: List[UpdateShippingRequest] = Field(..., description="송장 정보 목록")
