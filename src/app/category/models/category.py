from tortoise import fields
from tortoise.models import Model


class Category(Model):
    class Meta:
        table = 'category'
