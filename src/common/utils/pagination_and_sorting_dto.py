from pydantic import BaseModel, Field


class PaginationAndSortingDTO(BaseModel):
    page: int = Field(1, ge=1, description="페이지 번호 (1 이상)")
    page_size: int = Field(10, ge=1, le=100, description="페이지 크기 (1-100)")
    sort: str = Field("created_at", description="정렬 기준 필드")
    order: str = Field("desc", pattern="^(asc|desc)$", description="정렬 순서 (asc 또는 desc)")

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 10,
                "sort": "created_at",
                "order": "desc",
            }
        }
