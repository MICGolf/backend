from pydantic import BaseModel, Field


class BannerCreateRequest(BaseModel):
    """배너 생성 요청 DTO"""

    title: str = Field(..., description="배너 제목")
    sub_title: str = Field(..., description="배너 소제목")
    eventUrl: str = Field(..., description="클릭시 이동할 이벤트 URL")
    category_type: str = Field(..., description="배너 타입 (banner/promotion)")
    is_active: bool = Field(default=True, description="활성화 상태")


class BannerUpdateRequest(BaseModel):
    """배너 수정 요청 DTO"""

    title: str | None = Field(None, description="수정할 배너 제목")
    sub_title: str | None = Field(None, description="수정할 배너 소제목")
    event_url: str | None = Field(None, description="수정할 이벤트 URL")
    category_type: str | None = Field(None, description="수정할 배너 타입 (banner/promotion)")
    is_active: bool | None = Field(None, description="수정할 활성화 상태")
    display_order: int | None = Field(None, description="수정할 표시 순서")
