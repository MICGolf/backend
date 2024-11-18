from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="카테고리 이름")
    parent_id: Optional[int] = Field(None, description="상위 카테고리 ID")


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="카테고리 이름")
    parent_id: Optional[int] = Field(None, description="상위 카테고리 ID")
