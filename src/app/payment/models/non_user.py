from enum import Enum

from tortoise import fields
from tortoise.fields import ForeignKeyRelation

from common.models.base_model import BaseModel

# class OrderStatus(str, Enum):
#     """주문 상태 Enum"""
#
#     PENDING = "pending"  # 주문 대기
#     PAID = "paid"  # 결제 완료
#     FAILED = "failed"  # 결제 실패
#     CANCELLED = "cancelled"  # 주문 취소


class NonUserOrder(BaseModel):
    """비회원 주문 모델"""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=255)
    phone = fields.CharField(max_length=20)
    shipping_address = fields.CharField(max_length=255)
    detail_address = fields.CharField(max_length=255)
    request = fields.TextField(null=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    # status = fields.CharEnumField(OrderStatus, default=OrderStatus.PENDING)

    class Meta:
        table = "non_user_orders"


class NonUserOrderProduct(BaseModel):
    """비회원 주문 상품 모델"""

    id = fields.IntField(pk=True)
    non_user_order: ForeignKeyRelation["NonUserOrder"] = fields.ForeignKeyField(
        "models.NonUserOrder", related_name="order_products"
    )
    product_name = fields.CharField(max_length=255)
    product_price = fields.DecimalField(max_digits=10, decimal_places=2)
    quantity = fields.IntField()

    class Meta:
        table = "non_user_order_products"
