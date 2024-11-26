from enum import StrEnum

from tortoise import fields

from common.models.base_model import BaseModel


class BannerType(StrEnum):
    """배너와 프로모션 타입을 정의하는 열거형"""

    BANNER = "banner"  # 일반 배너
    PROMOTION = "promotion"  # 프로모션 배너


class Banner(BaseModel):
    """배너 정보를 저장하는 모델"""

    # 기본 정보 필드
    title = fields.CharField(max_length=255, description="배너 제목")
    sub_title = fields.CharField(max_length=255, description="배너 소제목")
    image_url = fields.CharField(max_length=255, description="배너 이미지 URL")
    event_url = fields.CharField(max_length=255, description="이벤트 URL")

    # 상태 및 분류 필드
    is_active = fields.BooleanField(default=True, description="활성화 상태")
    category_type = fields.CharEnumField(BannerType, max_length=20, description="배너 타입")
    display_order = fields.IntField(default=1, description="표시 순서")

    class Meta:
        table = "banner"
        ordering = ["category_type", "display_order", "-created_at"]

    @classmethod
    async def get_by_type(cls, banner_type: str | None = None) -> list["Banner"]:
        """타입별 배너 목록 조회"""
        query = cls.all().order_by("display_order", "-created_at")
        if banner_type:
            query = query.filter(category_type=banner_type)
        return await query
