from tortoise import fields
from tortoise.models import Model


class Banner(Model):
    class Meta:
        table = "banner"
