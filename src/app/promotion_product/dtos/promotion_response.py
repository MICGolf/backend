from typing import Optional

from pydantic import BaseModel


class PromotionProductResponse(BaseModel):
    id: Optional[int]
    product_code: str
    product_id: int
    product_name: str
    price: float
    promotion_type: str
    is_active: bool
    image_url: str


class PromotionProductListResponse(BaseModel):
    items: list[PromotionProductResponse]
    total: int
    page: int
    size: int
