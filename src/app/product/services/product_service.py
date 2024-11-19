import asyncio
import itertools
import os
import unicodedata
from datetime import datetime
from typing import List, Optional

from fastapi import UploadFile
from tortoise.expressions import Q

from app.category.models.category import Category, CategoryProduct
from app.category.services.category_services import CategoryService
from app.product.dtos.request import ProductWithOptionCreateRequestDTO
from app.product.dtos.response import OptionDTO, OptionImageDTO, ProductDTO, ProductResponseDTO
from app.product.models.product import CountProduct, Option, OptionImage, Product


class ProductService:
    @classmethod
    async def get_product_with_options(cls, product_id: int) -> ProductResponseDTO:
        product, options = await asyncio.gather(
            Product.get_by_id(product_id=product_id),
            Option.get_with_stock_and_images_by_product_id(product_id=product_id),
        )

        product_dto = ProductDTO.model_validate(product)
        option_dtos = cls.map_options_by_color(options)

        return ProductResponseDTO.build(product=product_dto, options=option_dtos)

    @classmethod
    async def get_products_with_options(
        cls,
        product_name: Optional[str] = None,
        product_id: Optional[int] = None,
        product_code: Optional[str] = None,
        sale_status: Optional[str] = None,
        category_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 10,
        sort: str = "created_at",
        order: str = "desc",
    ) -> list[ProductResponseDTO]:

        products, options = await cls._get_filtered_products_and_options(
            product_name=product_name,
            product_id=product_id,
            product_code=product_code,
            sale_status=sale_status,
            category_id=category_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            sort=sort,
            order=order,
        )

        product_map = {product.id: ProductDTO.model_validate(product) for product in products}  # type: ignore[attr-defined]
        product_options_map: dict[int | None, list[OptionDTO]] = {product_id: [] for product_id in product_map.keys()}

        for product_id, group_options in itertools.groupby(
            sorted(options, key=lambda x: x.product_id), key=lambda x: x.product_id  # type: ignore[attr-defined]
        ):
            product_options_map[product_id] = cls.map_options_by_color(list(group_options))

        product_response_dtos = [
            ProductResponseDTO.build(
                product=product_map[product_id],
                options=product_options_map.get(product_id, []),
            )
            for product_id in product_map.keys()
        ]

        return product_response_dtos

    @staticmethod
    def map_options_by_color(options: list[Option]) -> list[OptionDTO]:
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

        return [OptionDTO.model_validate(color) for color in color_options_map.values()]

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

    @staticmethod
    async def _get_filtered_products_and_options(
        product_name: Optional[str] = None,
        product_id: Optional[int] = None,
        product_code: Optional[str] = None,
        sale_status: Optional[str] = None,
        category_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 10,
        sort: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[Product], list[Option]]:
        filters = Q()

        if product_name:
            filters &= Q(name__icontains=product_name)
        if product_id:
            filters &= Q(id=product_id)
        if product_code:
            filters &= Q(product_code__icontains=product_code)
        if sale_status:
            filters &= Q(status=sale_status)
        if start_date:
            filters &= Q(created_at__gte=start_date)
        if end_date:
            filters &= Q(created_at__lte=end_date)

        if category_id:
            category_ids = await CategoryService.get_category_and_subcategories(category_id=category_id)
            filters &= Q(product_category__category_id__in=category_ids)

        if not filters:
            return await Product.all(), await Option.get_all_with_stock_and_images()

        offset = (page - 1) * page_size
        limit = page_size

        order_by = f"-{sort}" if order == "desc" else sort

        products = await Product.filter(filters).offset(offset).limit(limit).order_by(order_by)
        product_ids = [product.id for product in products]  # type: ignore[attr-defined]
        options = await Option.get_by_product_ids(product_ids=product_ids)

        return products, options
