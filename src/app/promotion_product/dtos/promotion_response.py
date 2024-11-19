from pydantic import BaseModel

from app.promotion_product.models.promotion_product import PromotionProduct


class PromotionProductResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    promotion_type: str
    is_active: bool


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float


class PromotionProductListResponse(BaseModel):
    items: list[PromotionProductResponse]
    total: int
    page: int
    size: int
