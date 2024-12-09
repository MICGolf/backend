from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.order.dtos.order_request import OrderSearchRequest


class ProductOptionResponse(BaseModel):
    size: str
    color: str
    color_code: Optional[str]
    price: Decimal


class OrderProductResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: Decimal
    option: ProductOptionResponse  # 옵션 정보 추가
    courier: Optional[str] = None
    tracking_number: Optional[str] = None
    shipping_status: Optional[str] = None
    procurement_status: Optional[str] = None
    claim_status: Optional[str] = None
    payment_status: Optional[str] = None
    current_status: Optional[str]  # 추가


class PaymentResponse(BaseModel):
    transaction_id: str
    order_id: int
    amount: Decimal
    payment_type: str
    payment_status: str
    paid_at: Optional[datetime]
    receipt_url: Optional[str]


class ShippingStatusResponse(BaseModel):
    status: str
    courier: str
    tracking_number: str
    tracking_url: Optional[str] = None  # Optional로 변경
    current_location: Optional[str] = None  # Optional로 변경
    updated_at: datetime


class OrderResponse(BaseModel):
    id: int
    order_number: str
    name: str
    phone: str
    shipping_address: str
    detail_address: Optional[str]
    request: Optional[str]
    total_amount: Decimal
    order_status: str
    created_at: datetime
    updated_at: datetime
    products: List[OrderProductResponse]
    payment: Optional[PaymentResponse]
    shipping: Optional[ShippingStatusResponse]


class OrderStatisticsResponse(BaseModel):
    total_orders: int
    new_orders: int  # 발주확인 처리 전
    confirmed_orders: int  # 발주확인 처리 후
    pending_orders: int  # 처리 대기 중
    shipping_orders: int
    completed_orders: int
    cancelled_orders: int


class OrderSearchResponse(BaseModel):
    orders: List[OrderResponse]  # 기존 OrderResponse 포함
    search_params: OrderSearchRequest  # 검색 조건도 포함
    total: int
    page: int
    limit: int
    total_pages: int


class UpdateOrderStatusResponse(BaseModel):
    order_id: int
    status: str
    updated_products_count: int
    message: str


class BatchUpdateStatusResponse(BaseModel):
    updated_count: int
    status: str


class VerifyOrderOwnerResponse(BaseModel):
    is_owner: bool
    message: str


class StockCheckResponse(BaseModel):
    has_sufficient_stock: bool
    available_quantity: int
    product_id: int
    option_id: int
    requested_quantity: int
    message: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    order: OrderResponse
    stock_check: StockCheckResponse


class PaginatedOrderResponse(BaseModel):
    orders: List[OrderResponse]  # 주문 목록
    total: int  # 총 주문 수
    page: int  # 현재 페이지
    limit: int  # 페이지 당 결과 수
    total_pages: int  # 총 페이지 수
