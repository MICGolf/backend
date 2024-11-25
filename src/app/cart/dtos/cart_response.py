from typing import List

from pydantic import BaseModel


class CartItemResponse(BaseModel):
    user_id: int
    product_id: int
    product_count: int


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_count: int
