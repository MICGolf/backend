from pydantic import BaseModel


class OptionImageDTO(BaseModel):
    id: int
    image_url: str

    class Config:
        from_attributes = True


class OptionSizeDTO(BaseModel):
    size: str
    stock: int


class OptionDTO(BaseModel):
    id: int
    color: str
    color_code: str
    images: list[OptionImageDTO]
    sizes: list[OptionSizeDTO]

    class Config:
        from_attributes = True


class ProductDTO(BaseModel):
    id: int
    name: str
    price: float
    discount: float
    origin_price: float
    description: str
    detail: str
    brand: str
    status: str
    product_code: str

    class Config:
        from_attributes = True


class ProductResponseDTO(BaseModel):
    product: ProductDTO
    options: list[OptionDTO]

    @classmethod
    def build(cls, product: ProductDTO, options: list[OptionDTO]) -> "ProductResponseDTO":
        return cls(product=product, options=options)
