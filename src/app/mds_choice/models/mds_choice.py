from tortoise import fields
from tortoise.models import Model


class MdsChoice(Model):
    class Meta:
        table_name = "mds_choice"
