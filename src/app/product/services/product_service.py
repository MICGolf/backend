import asyncio
import os
import unicodedata
from typing import List

from fastapi import UploadFile

from app.category.models.category import Category, CategoryProduct
from app.product.dtos.request import ProductWithOptionCreateRequestDTO
from app.product.dtos.response import OptionDTO, OptionImageDTO, ProductDTO, ProductResponseDTO
from app.product.models.product import CountProduct, Option, OptionImage, Product


class ProductService:
    @staticmethod
    async def get_product_with_options(product_id: int) -> ProductResponseDTO:
        product, options = await asyncio.gather(
            Product.get_by_id(product_id=product_id),
            Option.get_with_stock_and_images_by_product_id(product_id=product_id),
        )

        product_dto = ProductDTO.model_validate(product)

        color_options_map = {}

        for option in options:
            if option.color_code not in color_options_map:

                color_options_map[option.color_code] = {
                    "id": option.id,  # type: ignore[attr-defined]
                    "color": option.color,
                    "color_code": option.color_code,
                    "images": [
                        OptionImageDTO.model_validate(image) for image in option.images  # type: ignore[attr-defined]
                    ],
                    "sizes": [],
                }

            color_options_map[option.color_code]["sizes"].append(
                {"size": option.size, "stock": option.stock}  # type: ignore[attr-defined]
            )

        option_dtos = [OptionDTO.model_validate(color) for color in color_options_map.values()]

        return ProductResponseDTO.build(product=product_dto, options=option_dtos)

    @classmethod
    async def create_product_with_options(
        cls,
        product_create_dto: ProductWithOptionCreateRequestDTO,
        files: List[UploadFile],
        upload_dir: str,
    ) -> None:

        product_dto = product_create_dto.product
        option_dtos = product_create_dto.options
        image_mapping = product_create_dto.image_mapping
        category_id = product_create_dto.category_id

        product, category = await asyncio.gather(
            Product.create(**product_dto.model_dump()),
            Category.get(id=category_id),
        )

        options_to_create = [
            Option(
                product=product,
                color=option_dto.color,
                color_code=option_dto.color_code,
                size=size_option.size,
            )
            for option_dto in option_dtos
            for size_option in option_dto.sizes
        ]

        await asyncio.gather(
            CategoryProduct.create(category=category, product=product), Option.bulk_create(options_to_create)
        )

        created_options = await Option.filter(product=product).all()
        option_map = {(opt.color_code, opt.size): opt for opt in created_options}

        count_products_to_create = [
            CountProduct(
                product=product,
                option=option_map[(option_dto.color_code, size_option.size)],
                count=size_option.stock,
            )
            for option_dto in option_dtos
            for size_option in option_dto.sizes
        ]

        option_image_entries = await cls._process_images(created_options, image_mapping, files, upload_dir)

        await asyncio.gather(
            CountProduct.bulk_create(count_products_to_create), OptionImage.bulk_create(option_image_entries)
        )

    @staticmethod
    async def _process_images(
        options: list[Option],
        image_mapping: dict[str, list[str]],
        files: list[UploadFile],
        upload_dir: str,
    ) -> list[OptionImage]:

        option_image_entries = []

        for option in options:
            if option.color_code in image_mapping:
                file_names = image_mapping[option.color_code]
                for file_name in file_names:
                    matching_file = next(
                        (
                            file
                            for file in files
                            if unicodedata.normalize("NFC", file.filename or "")
                            == unicodedata.normalize("NFC", file_name or "")
                        ),
                        None,
                    )

                    if matching_file:
                        os.makedirs(upload_dir, exist_ok=True)
                        file_path = os.path.join(upload_dir, matching_file.filename or "")

                        with open(file_path, "wb") as f:
                            f.write(await matching_file.read())

                        option_image_entries.append(OptionImage(option=option, image_url=file_path))
        return option_image_entries
