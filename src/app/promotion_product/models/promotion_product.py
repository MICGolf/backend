from enum import Enum

from tortoise import fields

from common.models.base_model import BaseModel


class PromotionType(str, Enum):
    BEST = "best"
    MD_PICK = "md_pick"


class PromotionProduct(BaseModel):
    product = fields.ForeignKeyField(
        "models.Product", related_name="promotion", on_delete=fields.CASCADE
    )  # type: ignore
    promotion_type = fields.CharEnumField(PromotionType, max_length=10)  # best, md_pick
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "promotion_product"
