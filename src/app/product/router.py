import json
import os
import unicodedata

from fastapi import APIRouter, Body, File, HTTPException, UploadFile

from app.product.dtos.request import ProductWithOptionCreateRequestDTO
from app.product.dtos.response import ProductResponseDTO
from app.product.example_schema.create_request_example import (
    PRODUCT_CREATE_DESCRIPTION, PRODUCT_CREATE_REQUEST_EXAMPLE_SCHEMA)
from app.product.models.product import Option, OptionImage, Product
from core.configs import settings

router = APIRouter(prefix="/products", tags=["상품"])


@router.get(
    "/{product_code}",
    response_model=ProductResponseDTO,
)
async def get_product_handler(product_code: str) -> ProductResponseDTO:
    return ProductResponseDTO.model_validate(
        await Product.get_with_related_all_data(product_code=product_code)
    )


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

    validate_data = ProductWithOptionCreateRequestDTO(**request_data)

    product_dto = validate_data.product
    option_dtos = validate_data.option
    image_mapping = validate_data.image_mapping

    product = await Product.create(**product_dto.model_dump())

    for option_dto in option_dtos:
        option = await Option.create(**option_dto.model_dump(), product=product)

        if option.color_code in image_mapping:
            file_names = image_mapping[option.color_code]
            for file_name in file_names:
                matching_file = None
                for file in files:
                    normalized_filename = unicodedata.normalize(
                        "NFC", file.filename or ""
                    )
                    normalized_file_name = unicodedata.normalize("NFC", file_name or "")

                    if normalized_filename == normalized_file_name:
                        matching_file = file
                        break

                if matching_file:
                    upload_dir = settings.UPLOAD_DIR
                    os.makedirs(upload_dir, exist_ok=True)

                    unique_filename = matching_file.filename
                    file_path = os.path.join(upload_dir, unique_filename or "")

                    with open(file_path, "wb") as f:
                        f.write(await matching_file.read())

                    await OptionImage.create(option=option, image_url=file_path)
                else:
                    print(f"No matching file found for {file_name}")

    return
