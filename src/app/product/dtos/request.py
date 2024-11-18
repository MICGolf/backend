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
