import asyncio
import itertools
import os
import unicodedata
from datetime import datetime
from typing import Optional

from fastapi import UploadFile
from tortoise.expressions import Q

from app.category.models.category import Category, CategoryProduct
from app.category.services.category_services import CategoryService
from app.product.dtos.request import (
    OptionUpdateDTO,
    ProductUpdateDTO,
    ProductWithOptionCreateRequestDTO,
    ProductWithOptionUpdateRequestDTO,
)
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

        product_map = {product.id: ProductDTO.model_validate(product) for product in products}
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
        files: list[UploadFile],
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
        product_ids = [product.id for product in products]
        options = await Option.get_by_product_ids(product_ids=product_ids)

        return products, options

    @classmethod
    async def update_products_status(cls, product_ids: list[int], status: str) -> None:
        await Product.filter(id__in=product_ids).update(status=status)

    @staticmethod
    async def _update_product_basic_info(product_id: int, product_update_dto: ProductUpdateDTO) -> Product:
        product = await Product.get(id=product_id)
        await product.update_from_dict(product_update_dto.model_dump()).save()
        return product

    @staticmethod
    async def _update_category(product: Product, new_category_id: int) -> None:
        current_category_product = await CategoryProduct.filter(product=product).first()

        if current_category_product and current_category_product.category_id == new_category_id:  # type: ignore[attr-defined]
            return

        if current_category_product:
            await current_category_product.delete()

        new_category = await Category.get(id=new_category_id)
        await CategoryProduct.create(product=product, category=new_category)

    @staticmethod
    async def _update_options(product: Product, options_dto: list[OptionUpdateDTO]) -> dict[str, list[Option]]:
        existing_options = await Option.filter(product=product).all()
        existing_option_map = {(opt.color_code, opt.size): opt for opt in existing_options}

        options_to_create = []
        options_to_delete = []
        options_to_update = []

        updated_keys = {(opt.color_code, size.size) for opt in options_dto for size in opt.sizes}

        for key, option in existing_option_map.items():
            if key not in updated_keys:
                options_to_delete.append(option)

        for option_dto in options_dto:
            for size_dto in option_dto.sizes:
                key = (option_dto.color_code, size_dto.size)
                if key in existing_option_map:
                    option = existing_option_map[key]
                    option.color = option_dto.color
                    option.color_code = option_dto.color_code
                    option.size = size_dto.size
                    options_to_update.append(option)
                else:
                    options_to_create.append(
                        Option(
                            product=product,
                            color=option_dto.color,
                            color_code=option_dto.color_code,
                            size=size_dto.size,
                        )
                    )

        tasks = []

        if options_to_delete:
            tasks.append(Option.filter(pk__in=[opt.id for opt in options_to_delete]).delete())  # type: ignore
        if options_to_update:
            tasks.append(Option.bulk_update(options_to_update, fields=["color", "color_code", "size"]))  # type: ignore
        if options_to_create:
            tasks.append(Option.bulk_create(options_to_create))  # type: ignore

        if tasks:
            await asyncio.gather(*tasks)

        created_options = (
            await Option.filter(product=product).exclude(id__in=[opt.id for opt in existing_options]).all()  # type: ignore
        )

        return {
            "created": created_options,
            "updated": options_to_update,
            "deleted": options_to_delete,
        }

    @staticmethod
    async def _update_stock(product: Product, options_dto: list[OptionUpdateDTO]) -> None:
        existing_options = await Option.filter(product=product).all()
        existing_option_map = {(opt.color_code, opt.size): opt for opt in existing_options}

        count_products_to_create = []
        count_products_to_update = []

        for option_dto in options_dto:
            for size_dto in option_dto.sizes:
                key = (option_dto.color_code, size_dto.size)
                option = existing_option_map.get(key)
                if option:
                    _, created = await CountProduct.update_or_create(
                        product=product,
                        option=option,
                        defaults={"count": size_dto.stock},
                    )
                    if not created:
                        count_products_to_update.append(option)
                else:
                    count_products_to_create.append(
                        CountProduct(
                            product=product,
                            option=option,
                            count=size_dto.stock,
                        )
                    )

        tasks = []
        if count_products_to_create:
            tasks.append(CountProduct.bulk_create(count_products_to_create))
        if count_products_to_update:
            tasks.extend(count_products_to_update)  # type: ignore

        if tasks:
            await asyncio.gather(*tasks)

    @classmethod
    async def _update_images(
        cls,
        product: Product,
        options: list[Option],
        image_mapping: dict[str, list[str]],
        files: list[UploadFile],
        upload_dir: str,
    ) -> None:
        existing_images = await OptionImage.filter(option__product=product).all()
        images_to_keep = {img for color_code in image_mapping for img in image_mapping[color_code]}
        images_to_delete = [img for img in existing_images if img.image_url not in images_to_keep]

        for img in images_to_delete:
            try:
                os.remove(img.image_url)
            except FileNotFoundError:
                pass
            await img.delete()

        if files:
            new_images = await cls._process_images(options, image_mapping, files, upload_dir)
            await OptionImage.bulk_create(new_images)

    @classmethod
    async def update_product_with_options(
        cls,
        product_id: int,
        product_update_dto: ProductWithOptionUpdateRequestDTO,
        files: list[UploadFile],
        upload_dir: str,
    ) -> None:
        # 1. 기본 정보 업데이트
        product = await cls._update_product_basic_info(product_id, product_update_dto.product)

        # 2. 카테고리 업데이트
        await cls._update_category(product, product_update_dto.category_id)
        # 3. 옵션 업데이트
        updated_options = await cls._update_options(product, product_update_dto.options)

        # 4. 재고 업데이트
        await cls._update_stock(product, product_update_dto.options)

        # 5. 이미지 업데이트
        await cls._update_images(
            product,
            updated_options["created"] + updated_options["updated"],
            product_update_dto.image_mapping,
            files,
            upload_dir,
        )

    @classmethod
    async def delete_product(cls, product_id: int) -> None:

        product = await Product.get(id=product_id)

        await cls.delete_product_images(product_id)

        await product.delete()

    @classmethod
    async def delete_product_images(cls, product_id: int) -> None:
        images = await OptionImage.filter(option__product_id=product_id).all()

        async def delete_image_file(image: OptionImage) -> None:
            try:
                os.remove(image.image_url)
            except FileNotFoundError:
                pass

        await asyncio.gather(*(delete_image_file(image) for image in images))
