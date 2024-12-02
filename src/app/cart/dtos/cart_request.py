from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    product_id: int = Field(..., description="상품 ID")
    color: str = Field(..., description="상품 색상")
    size: str = Field(..., description="상품 크기")
    product_count: int = Field(..., description="상품 수량", ge=1)
