from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class OrderProductResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: Decimal
    courier: Optional[str] = None
    tracking_number: Optional[str] = None
    shipping_status: Optional[str] = None
    procurement_status: Optional[str] = None


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
    email: Optional[str] = None
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
