from enum import StrEnum

from tortoise import fields

from common.models.base_model import BaseModel


class BannerType(StrEnum):
    BANNER = "banner"
    PROMOTION = "promotion"


class Banner(BaseModel):
    title = fields.CharField(max_length=255)
    image_url = fields.CharField(max_length=255)
    redirect_url = fields.CharField(max_length=255, null=True)
    is_active = fields.BooleanField(default=True)
    banner_type = fields.CharEnumField(BannerType, max_length=20)
    display_order = fields.IntField(default=0)

    class Meta:
        table = "banner"
        ordering = ["banner_type", "display_order", "-created_at"]

    @classmethod
    async def get_by_type(cls, banner_type: str | None = None) -> list["Banner"]:
        query = cls.all()
        if banner_type:
            query = query.filter(banner_type=banner_type)
        return await query.order_by("display_order", "-created_at")
