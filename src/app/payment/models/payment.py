from enum import Enum
from typing import Any, Dict

from tortoise import fields
from tortoise.fields import ForeignKeyRelation

from app.order.models.order import NonUserOrder
from app.user.models.user import User
from common.models.base_model import BaseModel


class PaymentStatus(str, Enum):
    """결제 상태 Enum"""

    READY = "ready"  # 결제 대기
    RESERVED = "reserved"  # 결제 예약 상태 (덕배 Step 1)
    CHECKOUT = "checkout"  # 결제 요청 상태 (덕배 Step 2)
    PAID = "paid"  # 결제 완료 상태 (덕배 Step 3)
    FAILED = "failed"  # 결제 실패
    CANCELLED = "cancelled"  # 결제 취소


class PaymentMethod(str, Enum):
    """결제 수단 Enum"""

    CARD = "card"  # 신용카드
    TRANS = "trans"  # 실시간계좌이체
    VBANK = "vbank"  # 가상계좌
    PHONE = "phone"  # 휴대폰소액결제
    KAKAOPAY = "kakaopay"  # 카카오페이
    NAVERPAY = "naverpay"  # 네이버페이
    PAYCO = "payco"  # 페이코
    TOSSPAY = "tosspay"  # 토스페이


class PaymentType(str, Enum):
    """PG사 구분 Enum"""

    KAKAOPAY = "kakaopay"  # 카카오페이
    TOSSPAYMENTS = "tosspayments"  # 토스페이먼츠
    NAVERPAY = "naverpay"  # 네이버페이
    HTML5_INICIS = "html5_inicis"  # KG 이니시스


class BasePayment(BaseModel):
    """결제 기본 모델"""

    id = fields.IntField(pk=True)
    transaction_id = fields.CharField(max_length=100, unique=True)  # 주문번호
    merchant_uid = fields.CharField(max_length=100, unique=True)  # 포트원 주문번호
    imp_uid = fields.CharField(max_length=100, null=True)  # 포트원 결제 고유번호
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    payment_method = fields.CharEnumField(PaymentMethod)  # 결제 수단 필드 추가
    payment_type = fields.CharEnumField(PaymentType)  # PG사 구분
    status = fields.CharEnumField(PaymentStatus, default=PaymentStatus.READY)

    # 결제 처리 정보
    paid_at = fields.DatetimeField(null=True)
    failed_at = fields.DatetimeField(null=True)
    cancelled_at = fields.DatetimeField(null=True)
    fail_reason = fields.TextField(null=True)

    # 카드 정보
    card_number = fields.CharField(max_length=20, null=True)
    card_expiry = fields.CharField(max_length=7, null=True)
    approval_number = fields.CharField(max_length=100, null=True)

    # PG사 정보
    pg_provider = fields.CharField(max_length=20, default="kakaopay")
    pg_tid = fields.CharField(max_length=100, null=True)
    receipt_url = fields.CharField(max_length=255, null=True)

    class Meta:
        abstract = True


class UserPayment(BasePayment):
    """회원 결제 모델"""

    user: ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="payments", source_field="user_id"
    )
    customer_uid = fields.CharField(max_length=100, null=True)  # 카드 빌링키

    class Meta:
        table = "user_payments"

    async def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "merchant_uid": self.merchant_uid,
            "imp_uid": self.imp_uid,
            "amount": self.amount,
            "status": self.status,
            "payment_type": self.payment_type,
            "user_id": getattr(self, "user_id", None),
            "customer_uid": self.customer_uid,
            "pg_provider": self.pg_provider,
            "receipt_url": self.receipt_url,
            "approval_number": self.approval_number,
            "paid_at": self.paid_at,
            "pg_tid": self.pg_tid,
        }


class NonUserPayment(BasePayment):
    """비회원 결제 모델"""

    non_user_order: ForeignKeyRelation["NonUserOrder"] = fields.ForeignKeyField(
        "models.NonUserOrder", related_name="payments", source_field="non_user_order_id"
    )

    class Meta:
        table = "non_user_payments"

    async def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "merchant_uid": self.merchant_uid,
            "imp_uid": self.imp_uid,
            "amount": self.amount,
            "status": self.status,
            "payment_type": self.payment_type,
            "user_id": getattr(self, "non_user_order_id", None),
            "pg_provider": self.pg_provider,
            "receipt_url": self.receipt_url,
            "approval_number": self.approval_number,
            "paid_at": self.paid_at,
            "pg_tid": self.pg_tid,
        }
