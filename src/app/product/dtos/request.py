from pydantic import BaseModel, Field

from app.product.example_schema.create_request_example import (
    OPTION_CREATE_SCHEMA, PRODUCT_CREATE_REQUEST_SCHEMA, PRODUCT_CREATE_SCHEMA)


class OptionDTO(BaseModel):
    size: str
    color: str
    color_code: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    stock: int = Field(..., ge=0)

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
    product: ProductDTO
    option: list[OptionDTO]
    image_mapping: dict[str, list[str]]

    class Config:
        json_schema_extra = PRODUCT_CREATE_REQUEST_SCHEMA
