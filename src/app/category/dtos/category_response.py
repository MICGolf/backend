from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    depth: int
    created_at: datetime
    updated_at: datetime


class CategoryDetailResponse(CategoryResponse):
    product_count: int  # 해당 카테고리의 상품 수
    is_active: bool  # 카테고리 활성화 여부


class CategoryWithSubcategoriesResponse(CategoryResponse):
    subcategories: List["CategoryWithSubcategoriesResponse"] = []


class CategoryListResponse(BaseModel):
    total: int
    categories: List[CategoryResponse]
