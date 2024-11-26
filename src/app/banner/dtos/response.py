from datetime import datetime
from typing import TYPE_CHECKING, Generic, List, TypeVar

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.banner.models.banner import Banner

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    """페이지네이션된 응답을 위한 기본 DTO"""

    items: List[T]
    total: int  # 전체 항목 수
    page: int  # 현재 페이지
    page_size: int  # 페이지당 항목 수


class BannerResponse(BaseModel):
    """배너 정보를 반환하기 위한 DTO"""

    id: int = Field(..., description="배너 ID")
    title: str = Field(..., description="배너 제목")
    sub_title: str = Field(..., description="배너 소제목", alias="sub_title")
    image_url: str = Field(..., description="배너 이미지 URL")
    event_url: str = Field(..., description="이벤트 URL", alias="eventUrl")
    category_type: str = Field(..., description="배너 타입", alias="category_type")
    is_active: bool = Field(..., description="활성화 상태")
    display_order: int = Field(..., description="표시 순서")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")

    class Config:
        from_attributes = True
        populate_by_name = True

    @classmethod
    def from_banner(cls, banner: "Banner") -> "BannerResponse":
        """Banner 모델을 DTO로 변환"""
        return cls.model_validate(banner)


class BannerListResponse(PageResponse[BannerResponse]):
    """페이지네이션된 배너 목록 응답"""

    pass
