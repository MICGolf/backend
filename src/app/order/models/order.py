from tortoise import fields

from common.models.base_model import BaseModel


class NonUserOrder(BaseModel):
    name = fields.CharField(max_length=255)
    phone = fields.CharField(max_length=20)
    shipping_address = fields.CharField(max_length=255)
    detail_address = fields.CharField(max_length=255, null=True)
    request = fields.TextField(null=True)

    class Meta:
        table = "non_user_order"


class NonUserOrderProduct(BaseModel):
    order = fields.ForeignKeyField(
        "models.NonUserOrder",
        related_name="order_product",
        on_delete=fields.CASCADE,
    )  # type: ignore
    product = fields.ForeignKeyField(
        "models.Product",
        related_name="product_order",
        on_delete=fields.CASCADE,
    )  # type: ignore

    option_id = fields.IntField(null=True)  # 추가
    quantity = fields.IntField(default=1)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    courier = fields.CharField(max_length=255, null=True)
    shipping_id = fields.CharField(max_length=255, null=True)
    current_status = fields.CharField(max_length=255, null=True)
    procurement_status = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "non_user_order_product"


class NonUserPayment(BaseModel):
    order = fields.ForeignKeyField(
        "models.NonUserOrder",
        related_name="payment",
        on_delete=fields.CASCADE,
    )  # type: ignore
    transaction_id = fields.CharField(max_length=255, unique=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    payment_type = fields.CharField(max_length=50)
    payment_status = fields.CharField(max_length=50)

    class Meta:
        table = "non_user_payment"
