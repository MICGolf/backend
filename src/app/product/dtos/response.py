from pydantic import BaseModel


class OptionImageDTO(BaseModel):
    id: int
    image_url: str

    class Config:
        from_attributes = True


class CountProductDTO(BaseModel):
    id: int
    count: int

    class Config:
        from_attributes = True


class OptionDTO(BaseModel):
    id: int
    size: str
    color: str
    color_code: str
    images: list[OptionImageDTO]
    option_stock: list[CountProductDTO]

    class Config:
        from_attributes = True


class ProductResponseDTO(BaseModel):
    id: int
    name: str
    product_code: str
    options: list[OptionDTO]

    class Config:
        from_attributes = True
