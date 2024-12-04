from typing import List

from pydantic import BaseModel


class CartItemResponse(BaseModel):
    cart_id: int
    user_id: int
    product_id: int
    option_id: int
    product_code: str
    product_name: str
    product_image_url: str
    product_color: str
    product_size: str
    product_amount: int
    product_stock: int
    origin_price: float
    price: float
    discount: int
    discount_option: str


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_count: int
