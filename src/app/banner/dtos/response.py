from datetime import datetime
from typing import TYPE_CHECKING, Generic, List, TypeVar

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.banner.models.banner import Banner  # 순환 참조 방지를 위한 조건부 임포트

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    """페이지네이션 응답 DTO

    Attributes:
        items (List[T]): 페이지 항목 목록
        total (int): 전체 항목 수
        page (int): 현재 페이지 번호
        page_size (int): 페이지 크기
    """

    items: List[T]
    total: int
    page: int
    page_size: int


class BannerResponse(BaseModel):
    """배너 응답 DTO"""

    id: int = Field(..., description="배너 ID")
    title: str = Field(..., description="배너 제목")
    sub_title: str = Field(..., description="배너 소제목", alias="subTitle")
    image_url: str = Field(..., description="배너 이미지 URL")
    event_url: str = Field(..., description="이벤트 URL", alias="eventUrl")
    category_type: str = Field(..., description="배너 타입", alias="banner_type")
    is_active: bool = Field(..., description="활성화 상태")
    display_order: int = Field(..., description="표시 순서")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")

    class Config:
        from_attributes = True
        populate_by_name = True

    @classmethod
    def from_banner(cls, banner: "Banner") -> "BannerResponse":
        """Banner 모델을 응답 DTO로 변환

        Args:
            banner: Banner 모델 인스턴스

        Returns:
            BannerResponse: 변환된 응답 DTO
        """
        return cls.model_validate(banner)


class BannerListResponse(PageResponse[BannerResponse]):
    """배너 목록 페이지네이션 응답"""

    pass
