from enum import StrEnum

from tortoise import fields

from common.models.base_model import BaseModel


class BannerType(StrEnum):
    """배너 타입 정의

    Attributes:
        BANNER: 일반 배너
        PROMOTION: 프로모션 배너
    """

    BANNER = "banner"
    PROMOTION = "promotion"


class Banner(BaseModel):
    """배너 모델"""
    title = fields.CharField(max_length=255, description="배너 제목")
    sub_title = fields.CharField(max_length=255, description="배너 소제목")
    image_url = fields.CharField(max_length=255, description="배너 이미지 URL")
    event_url = fields.CharField(max_length=255, description="이벤트 URL")
    is_active = fields.BooleanField(default=True, description="활성화 상태") # 기본값 True
    category_type = fields.CharEnumField(BannerType, max_length=20, description="배너 타입")
    display_order = fields.IntField(default=1, description="표시 순서") # 1부터 시작

    class Meta:
        table = "banner"
        ordering = ["category_type", "display_order", "-created_at"]

    @classmethod
    async def get_by_type(cls, banner_type: str | None = None) -> list["Banner"]:
        """배너 타입별 조회

        Args:
            banner_type: 조회할 배너 타입 (banner/promotion)

        Returns:
            배너 목록 (표시 순서, 생성일시 순 정렬)
        """
        query = cls.all().order_by("display_order", "-created_at")
        if banner_type:
            query = query.filter(category_type=banner_type)
        return await query
