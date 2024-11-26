from enum import StrEnum

from tortoise import fields
from tortoise.fields import ReverseRelation
from tortoise.functions import Sum

from app.category.models.category import CategoryProduct
from common.models.base_model import BaseModel


class DiscountOption(StrEnum):
    PERCENT = "percent"  # 퍼센트 할인
    AMOUNT = "amount"  # 금액 할인


class Product(BaseModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    discount = fields.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_option = fields.CharEnumField(DiscountOption, max_length=10, default=DiscountOption.PERCENT)
    origin_price = fields.DecimalField(max_digits=10, decimal_places=2)
    description = fields.TextField(null=True)
    detail = fields.TextField(null=True)
    brand = fields.CharField(max_length=255, default="micgolf")
    status = fields.CharField(max_length=1, default="Y")  # Y, N
    product_code = fields.CharField(max_length=255, unique=True)

    options: ReverseRelation["Option"]
    categories: fields.ReverseRelation["CategoryProduct"]

    class Meta:
        table = "product"

    @classmethod
    async def get_by_id(cls, product_id: int) -> "Product":
        return await cls.get(id=product_id)


class Option(BaseModel):
    id = fields.IntField(pk=True)
    size = fields.CharField(max_length=255)
    color = fields.CharField(max_length=255)
    color_code = fields.CharField(max_length=255, null=True)
    product: fields.ForeignKeyRelation["Product"] = fields.ForeignKeyField(
        "models.Product", related_name="options", on_delete=fields.CASCADE
    )
    images: ReverseRelation["OptionImage"]

    class Meta:
        table = "option"

    @classmethod
    async def get_with_stock_and_images_by_product_id(cls, product_id: int) -> list["Option"]:
        return (
            await cls.filter(product__id=product_id)
            .annotate(stock=Sum("option_stock__count"))
            .prefetch_related("images")
        )

    @classmethod
    async def get_all_with_stock_and_images(cls) -> list["Option"]:
        return await cls.all().annotate(stock=Sum("option_stock__count")).prefetch_related("images")

    @classmethod
    async def get_by_product_ids(cls, product_ids: list[int]) -> list["Option"]:
        return (
            await cls.filter(product__id__in=product_ids)
            .annotate(stock=Sum("option_stock__count"))
            .prefetch_related("images")
        )


class OptionImage(BaseModel):
    id = fields.IntField(pk=True)
    image_url = fields.CharField(max_length=255)
    option: fields.ForeignKeyRelation["Option"] = fields.ForeignKeyField(
        "models.Option", related_name="images", on_delete=fields.CASCADE
    )

    class Meta:
        table = "option_image"


class CountProduct(BaseModel):
    id = fields.IntField(pk=True)
    product: fields.ForeignKeyRelation["Product"] = fields.ForeignKeyField(
        "models.Product", related_name="product_stock", on_delete=fields.CASCADE
    )
    option: fields.ForeignKeyRelation["Option"] = fields.ForeignKeyField(
        "models.Option", related_name="option_stock", on_delete=fields.CASCADE
    )
    count = fields.IntField(default=0)

    class Meta:
        table = "count_product"
