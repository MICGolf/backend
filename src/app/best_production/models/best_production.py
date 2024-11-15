from tortoise import fields
from tortoise.models import Model


class BestProduction(Model):
    product_id = fields.IntField(pk=True)
    is_active = fields.BooleanField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'best_production'
