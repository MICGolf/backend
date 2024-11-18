from tortoise import fields

from common.models.base_model import BaseModel


class Product(BaseModel):
    name = fields.CharField(max_length=255)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    discount = fields.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    origin_price = fields.DecimalField(max_digits=10, decimal_places=2)
    description = fields.TextField(null=True)
    detail = fields.TextField(null=True)
    brand = fields.CharField(max_length=255, default="micgolf")
    status = fields.CharField(max_length=1, default="Y")  # Y, N
    product_code = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = "product"

    @classmethod
    async def get_with_related_all_data(cls, product_code: str) -> "Product":
        return await cls.get(product_code=product_code).prefetch_related(
            "options",
            "options__images",
            "options__option_stock",
        )


class Option(BaseModel):
    size = fields.CharField(max_length=255)
    color = fields.CharField(max_length=255)
    color_code = fields.CharField(max_length=255, null=True)
    product = fields.ForeignKeyField("models.Product", related_name="options", on_delete=fields.CASCADE)  # type: ignore

    class Meta:
        table = "option"


class OptionImage(BaseModel):
    image_url = fields.CharField(max_length=255)
    option = fields.ForeignKeyField("models.Option", related_name="images", on_delete=fields.CASCADE)  # type: ignore

    class Meta:
        table = "option_image"


class CountProduct(BaseModel):
    product = fields.ForeignKeyField("models.Product", related_name="product_stock", on_delete=fields.CASCADE)  # type: ignore
    option = fields.ForeignKeyField("models.Option", related_name="option_stock", on_delete=fields.CASCADE)  # type: ignore
    count = fields.IntField(default=0)

    class Meta:
        table = "count_product"
