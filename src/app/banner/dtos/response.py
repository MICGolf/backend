from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.banner.models.banner import Banner  # 순환 참조 방지를 위한 조건부 임포트


class BannerResponse(BaseModel):
    """배너 응답"""

    id: int = Field(..., description="배너 ID")
    title: str = Field(..., description="배너 제목")
    image_url: str = Field(..., description="배너 이미지 URL")
    redirect_url: str | None = Field(None, description="리다이렉트 URL")
    banner_type: str = Field(..., description="배너 타입")
    is_active: bool = Field(..., description="활성화 상태")
    display_order: int = Field(..., description="표시 순서")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")

    class Config:
        from_attributes = True

    @classmethod
    def from_banner(cls, banner: "Banner") -> "BannerResponse":
        return cls.model_validate(banner)
