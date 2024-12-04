from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    product_id: int = Field(..., description="상품 ID")
    option_id: int = Field(..., description="옵션 ID")
    product_count: int = Field(description="상품 수량", ge=1)
