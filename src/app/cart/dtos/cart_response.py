from typing import List

from pydantic import BaseModel


class CartItemResponse(BaseModel):
    user_id: int
    product_id: int
    product_name: str
    product_count: int
    product_color: str
    product_size: str
    product_price: float
    product_image_url: str


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_count: int
