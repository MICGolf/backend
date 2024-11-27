from tortoise import fields

from common.models.base_model import BaseModel


class User(BaseModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    phone = fields.CharField(max_length=20, null=True)
    login_id = fields.CharField(max_length=255, unique=True)
    user_type = fields.CharField(max_length=10, default="guest")  # guest, admin
    password = fields.CharField(max_length=255)
    social_login_type = fields.CharField(max_length=50, null=True)
    social_id = fields.CharField(max_length=255, null=True)
    refresh_token_id = fields.CharField(max_length=255, null=True)
    withdraw_period = fields.DatetimeField(null=True)
    status = fields.BooleanField(default=True)

    class Meta:
        table = "user"
        table_description = "User table"
