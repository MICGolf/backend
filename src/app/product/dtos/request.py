from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.product.example_schema.create_request_example import (
    OPTION_CREATE_SCHEMA,
    PRODUCT_CREATE_REQUEST_SCHEMA,
    PRODUCT_CREATE_SCHEMA,
)


class SizeOptionDTO(BaseModel):
    size: str
    stock: int = Field(..., ge=0)

    class Config:
        json_schema_extra = {"example": {"size": "M", "stock": 50}}


class OptionDTO(BaseModel):
    color: str
    color_code: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    sizes: list[SizeOptionDTO]

    class Config:
        json_schema_extra = OPTION_CREATE_SCHEMA


class ProductDTO(BaseModel):
    name: str
    price: float = Field(..., gt=0)
    discount: float = Field(..., ge=0, le=1)
    origin_price: float = Field(..., gt=0)
    description: str
    detail: str
    product_code: str

    class Config:
        json_schema_extra = PRODUCT_CREATE_SCHEMA


class ProductWithOptionCreateRequestDTO(BaseModel):
    category_id: int
    product: ProductDTO
    options: list[OptionDTO]
    image_mapping: dict[str, list[str]]

    class Config:
        json_schema_extra = PRODUCT_CREATE_REQUEST_SCHEMA


class ProductFilterRequestDTO(BaseModel):
    product_name: Optional[str] = Field(None, description="검색할 제품 이름", example="Smartphone")
    product_id: Optional[int] = Field(None, description="특정 제품의 ID", example=123)
    product_code: Optional[str] = Field(None, description="검색할 제품 코드", example="SP12345")
    sale_status: Optional[str] = Field(None, description="판매 상태 (예: available, sold_out 등)", example="available")
    category_id: Optional[int] = Field(None, description="카테고리 ID", example=5)
    start_date: Optional[datetime] = Field(None, description="검색 시작 날짜 (YYYY-MM-DD 형식)", example="2024-01-01")
    end_date: Optional[datetime] = Field(None, description="검색 종료 날짜 (YYYY-MM-DD 형식)", example="2024-12-31")
