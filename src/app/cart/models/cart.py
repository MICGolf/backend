from tortoise import fields

from common.models.base_model import BaseModel


class Cart(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="cart", on_delete=fields.CASCADE)  # type: ignore
    product = fields.ForeignKeyField("models.Product", related_name="cart_item", on_delete=fields.CASCADE)  # type: ignore
    product_count = fields.IntField(default=1)

    class Meta:
        table = "cart"
        unique_together = ("user", "product")  # 유니크 제약조건
