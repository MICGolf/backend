from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    product_id: int = Field(..., description="상품 ID")
    option_id: int = Field(..., description="옵션 ID")
    product_count: int = Field(description="상품 수량", ge=1)


class CartItemAddRequest(BaseModel):
    product_id: int = Field(..., description="상품 ID")
    color: str = Field(..., description="색상")
    size: str = Field(..., description="사이즈")
    product_count: int = Field(..., description="상품 수량", ge=1)
