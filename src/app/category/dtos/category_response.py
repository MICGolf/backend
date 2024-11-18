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


class CategoryWithSubcategoriesResponse(CategoryResponse):
    subcategories: List["CategoryWithSubcategoriesResponse"] = []


class CategoryListResponse(BaseModel):
    total: int
    categories: List[CategoryResponse]
