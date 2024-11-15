from tortoise import fields
from tortoise.models import Model


class Category(Model):
    name = fields.CharField(max_length=20)

    class Meta:
        table = "category"
