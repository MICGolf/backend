import json

from fastapi import APIRouter, Body, File, HTTPException, UploadFile

from app.product.dtos.request import ProductWithOptionCreateRequestDTO
from app.product.dtos.response import ProductResponseDTO
from app.product.example_schema.create_request_example import (
    PRODUCT_CREATE_DESCRIPTION,
    PRODUCT_CREATE_REQUEST_EXAMPLE_SCHEMA,
)
from app.product.services.product_service import ProductService
from core.configs import settings

router = APIRouter(prefix="/products", tags=["상품"])


@router.get(
    "/{product_code}",
    response_model=ProductResponseDTO,
)
async def get_product_handler(product_code: str) -> ProductResponseDTO:
    return await ProductService.get_product_with_options(product_code=product_code)


@router.post("", description=PRODUCT_CREATE_DESCRIPTION)
async def create_products_handler(
    request: str = Body(
        media_type="application/json",
        examples=[
            PRODUCT_CREATE_REQUEST_EXAMPLE_SCHEMA,
        ],
    ),
    files: list[UploadFile] = File(...),
) -> None:
    request_data = json.loads(request)

    return await ProductService.create_product_with_options(
        product_create_dto=ProductWithOptionCreateRequestDTO(**request_data),
        files=files,
        upload_dir=settings.UPLOAD_DIR,
    )
