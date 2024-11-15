from tortoise import fields
from tortoise.models import Model


class Product(Model):
    class Meta:
        table = "product"
