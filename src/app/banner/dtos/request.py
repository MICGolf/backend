from pydantic import BaseModel, Field


class BannerCreateRequest(BaseModel):
    """배너 생성 요청"""

    title: str = Field(..., description="배너 제목")
    redirect_url: str | None = Field(None, description="클릭시 이동할 URL")
    banner_type: str = Field(..., description="배너 타입 (banner/promotion)")
    is_active: bool = Field(default=True, description="활성화 상태")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "신상품 출시 배너",
                "redirect_url": "https://example.com/new",
                "banner_type": "banner",
                "is_active": True,
            }
        }


class BannerUpdateRequest(BaseModel):
    """배너 수정 요청"""

    title: str | None = Field(None, description="수정할 배너 제목")
    redirect_url: str | None = Field(None, description="수정할 리다이렉트 URL")
    is_active: bool | None = Field(None, description="수정할 활성화 상태")
    display_order: int | None = Field(None, description="수정할 표시 순서")
