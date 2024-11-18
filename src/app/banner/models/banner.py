from tortoise import fields

from common.models.base_model import BaseModel


class Banner(BaseModel):
    title = fields.CharField(max_length=255)
    image_url = fields.CharField(max_length=255)
    redirect_url = fields.CharField(max_length=255, null=True)
    is_active = fields.BooleanField(default=True)
    banner_type = fields.CharField(max_length=10)  # banner, promotion

    class Meta:
        table = "banner"
