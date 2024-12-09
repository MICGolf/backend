from enum import StrEnum

from tortoise import fields
from tortoise.fields import ForeignKeyRelation

from app.order.models.order import NonUserOrder
from common.models.base_model import BaseModel


class NonUserPayment(BaseModel):
    id = fields.IntField(pk=True)
    transaction_id = fields.CharField(max_length=255, unique=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    payment_type = fields.CharField(max_length=50)
    payment_status = fields.CharField(max_length=50)

    fail_reason = fields.TextField(null=True)
    approval_number = fields.CharField(max_length=100, null=True)

    order: ForeignKeyRelation["NonUserOrder"] = fields.ForeignKeyField(
        "models.NonUserOrder",
        related_name="payment",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "non_user_payment"


# class UserPayment(BaseModel):
#     pass


# class UserPayment(BaseModel):
#     transaction_id = fields.CharField(max_length=255, unique=True)
#     amount = fields.DecimalField(max_digits=10, decimal_places=2)
#     payment_type = fields.CharField(max_length=50)
#     payment_status = fields.CharField(max_length=50)
#
#     fail_reason = fields.TextField(null=True)
#     approval_number = fields.CharField(max_length=100, null=True)
#
#     order: ForeignKeyRelation["UserOrder"] = fields.ForeignKeyField(
#         "models.UserOrder",
#         related_name="payment",
#         on_delete=fields.CASCADE,
#     )  # type: ignore
#     user: ForeignKeyRelation["User"] = fields.ForeignKeyField(
#         "models.User",
#         related_name="payments",
#     )
#
#     class Meta:
#         table = "user_payment"


class PaymentStatus(StrEnum):
    """결제 상태 Enum"""

    RESERVED = "reserved"  # 결제 예약 상태 (덕배 Step 1)
    CHECKOUT = "checkout"  # 결제 요청 상태 (덕배 Step 2)
    PAID = "paid"  # 결제 완료 상태 (덕배 Step 3)
    FAILED = "failed"  # 결제 실패
    CANCELLED = "cancelled"  # 결제 취소


class PaymentType(StrEnum):
    """PG사 구분 Enum"""

    KAKAO_PAY = "kakao_pay"  # 카카오페이
    TOSS_PAYMENTS = "toss_payments"  # 토스페이먼츠
    NAVER_PAY = "naver_pay"  # 네이버페이
    KG_INICIS = "kg_inicis"  # KG 이니시스
