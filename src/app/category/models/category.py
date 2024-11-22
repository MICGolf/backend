from tortoise import fields

from common.models.base_model import BaseModel


class Category(BaseModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    parent = fields.ForeignKeyField(
        "models.Category",
        related_name="subcategory",
        null=True,
        on_delete=fields.CASCADE,
    )  # type: ignore
    depth = fields.IntField(default=0)

    class Meta:
        table = "category"


class CategoryProduct(BaseModel):
    category = fields.ForeignKeyField(
        "models.Category",
        related_name="category_product",
        on_delete=fields.CASCADE,
    )  # type: ignore
    product = fields.ForeignKeyField(
        "models.Product",
        related_name="product_category",
        on_delete=fields.CASCADE,
    )  # type: ignore

    class Meta:
        table = "category_product"
