import asyncio
import itertools
import unicodedata
from datetime import datetime
from io import BytesIO
from typing import Any, Coroutine, Optional, Union
from uuid import uuid4

from fastapi import UploadFile
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from app.category.models.category import Category, CategoryProduct
from app.category.services.category_services import CategoryService
from app.product.dtos.request import (
    OptionUpdateDTO,
    ProductUpdateDTO,
    ProductWithOptionCreateRequestDTO,
    ProductWithOptionUpdateRequestDTO,
)
from app.product.dtos.response import OptionDTO, OptionImageDTO, ProductDTO, ProductResponseDTO, ProductsResponseDTO
from app.product.models.product import CountProduct, Option, OptionImage, Product
from common.exceptions.custom_exceptions import MaxImageSizeExceeded, MaxImagesPerColorExceeded
from common.utils.ncp_s3_client import get_object_storage_client
from core.configs import settings


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
    ) -> ProductsResponseDTO:

        products, options, total_count = await cls._get_filtered_products_and_options(
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

        return ProductsResponseDTO.build(products=product_response_dtos, total_count=total_count)

    @staticmethod
    def map_options_by_color(options: list[Option]) -> list[OptionDTO]:
        color_options_map = {}

        for option in options:
            if option.color_code not in color_options_map:
                color_options_map[option.color_code] = {
                    "id": option.id,
                    "color": option.color,
                    "color_code": option.color_code,
                    "images": [OptionImageDTO.model_validate(image) for image in option.images],
                    "sizes": [],
                }

            color_options_map[option.color_code]["sizes"].append({"size": option.size, "stock": option.stock})  # type: ignore[attr-defined]

        return [OptionDTO.model_validate(color) for color in color_options_map.values()]

    @classmethod
    async def create_product_with_options(
        cls,
        product_create_dto: ProductWithOptionCreateRequestDTO,
        files: list[UploadFile],
    ) -> None:

        product_dto = product_create_dto.product
        option_dtos = product_create_dto.options
        image_mapping = product_create_dto.image_mapping
        category_id = product_create_dto.category_id

        await cls._validate_images(files, image_mapping)

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
            CategoryProduct.create(category=category, product=product),
            Option.bulk_create(options_to_create),
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

        option_image_entries = await cls._process_images(created_options, image_mapping, files)

        await asyncio.gather(
            CountProduct.bulk_create(count_products_to_create),
            OptionImage.bulk_create(option_image_entries),
        )

    @classmethod
    async def _validate_images(cls, files: list[UploadFile], image_mapping: dict[str, list[str]]) -> None:
        allowed_extensions = ["image/jpeg", "image/jpg", "image/png"]
        max_size_per_color = 2 * 1024 * 1024
        max_images_per_color = 6

        color_image_sizes = {}
        color_image_count = {}

        for file in files:
            if file.content_type not in allowed_extensions:
                raise ValueError(f"Invalid image type: {file.content_type}. Only JPEG and PNG are allowed.")

            file.file.seek(0)
            file_size = len(file.file.read())

            color_code = None
            for key, values in image_mapping.items():
                if file.filename in values:
                    color_code = key
                    break

            if not color_code:
                raise ValueError(f"Image {file.filename} does not have a valid color code mapping.")

            if color_code not in color_image_sizes:
                color_image_sizes[color_code] = 0
                color_image_count[color_code] = 0

            if color_image_count[color_code] >= max_images_per_color:
                raise MaxImagesPerColorExceeded(color_code=color_code, max_images=max_images_per_color)

            color_image_sizes[color_code] += file_size
            color_image_count[color_code] += 1

            if color_image_sizes[color_code] > max_size_per_color:
                raise MaxImageSizeExceeded(color_code=color_code, max_size=max_size_per_color)

    @staticmethod
    async def _process_images(
        options: list[Option],
        image_mapping: dict[str, list[str]],
        files: list[UploadFile],
    ) -> list[OptionImage]:
        object_storage_client = get_object_storage_client()
        option_image_entries = []
        upload_tasks = []
        uploaded_urls_map: dict[Any, Any] = {}  # 색상별 업로드된 URL 캐싱

        # 파일 내용을 미리 읽어서 안전하게 복사
        file_map = {}
        for file in files:
            content = await file.read()  # 파일 내용을 읽어 메모리에 저장
            file_map[unicodedata.normalize("NFC", file.filename or "")] = BytesIO(content)

        # 색상별로 이미지 업로드 작업 처리
        for color_code, file_names in image_mapping.items():
            if color_code not in uploaded_urls_map:  # 이미 처리되지 않은 색상만 처리
                uploaded_urls_map[color_code] = []  # 색상별 업로드 URL 리스트 초기화
                for file_name in file_names:
                    normalized_file_name = unicodedata.normalize("NFC", file_name or "")
                    file_obj = file_map.get(normalized_file_name)

                    if file_obj:
                        # 파일 포인터를 항상 처음으로 이동
                        file_obj.seek(0)

                        unique_file_name = f"{uuid4()}_{normalized_file_name}"
                        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

                        upload_task = object_storage_client.upload_file_obj(
                            bucket_name=bucket_name,
                            file_obj=file_obj,
                            object_name=f"images/{unique_file_name}",
                        )
                        upload_tasks.append((upload_task, color_code))  # 작업과 색상 코드 매핑

        print(f"Number of upload tasks: {len(upload_tasks)}")

        # 업로드 작업 수행 및 에러 처리
        upload_results = await asyncio.gather(*[task[0] for task in upload_tasks], return_exceptions=True)

        # 업로드 결과를 색상 코드별로 매핑
        for result, (_, color_code) in zip(upload_results, upload_tasks):
            if isinstance(result, Exception):
                print(f"Error occurred during upload for color {color_code}: {result}")
            else:
                print(f"Uploaded URL: {result}")
                uploaded_urls_map[color_code].append(result)

        # 옵션과 업로드된 이미지를 연결
        for option in options:
            if option.color_code in uploaded_urls_map:
                for uploaded_url in uploaded_urls_map[option.color_code]:
                    option_image_entries.append(OptionImage(option=option, image_url=uploaded_url))

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
    ) -> tuple[list[Product], list[Option], int]:
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

        offset = (page - 1) * page_size
        limit = page_size

        order_by = f"-{sort}" if order == "desc" else sort

        products = await Product.filter(filters).offset(offset).limit(limit).order_by(order_by)
        total_count = await Product.filter(filters).count()

        product_ids = [product.id for product in products]
        options = await Option.get_by_product_ids(product_ids=product_ids)

        return products, options, total_count

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
        current_category_product = await CategoryProduct.filter(product=product).prefetch_related("category").first()

        if current_category_product and current_category_product.category.id == new_category_id:
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
            tasks.append(Option.filter(pk__in=[opt.id for opt in options_to_delete]).delete())
        if options_to_update:
            tasks.append(Option.bulk_update(options_to_update, fields=["color", "color_code", "size"]))  # type: ignore
        if options_to_create:
            tasks.append(Option.bulk_create(options_to_create))  # type: ignore

        if tasks:
            await asyncio.gather(*tasks)

        created_options = (
            await Option.filter(product=product).exclude(id__in=[opt.id for opt in existing_options]).all()
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
    ) -> None:
        existing_images = await OptionImage.filter(option__product=product).all()

        images_to_keep = {img for color_code in image_mapping for img in image_mapping[color_code]}
        images_to_delete = [img for img in existing_images if img.image_url not in images_to_keep]

        await cls._delete_images(images_to_delete)

        if files:
            new_images = await cls._process_images(options, image_mapping, files)
            await OptionImage.bulk_create(new_images)

    @classmethod
    async def update_product_with_options(
        cls,
        product_id: int,
        product_update_dto: ProductWithOptionUpdateRequestDTO,
        files: list[UploadFile],
    ) -> None:
        # 1. 기본 정보 업데이트
        product = await cls._update_product_basic_info(product_id, product_update_dto.product)

        # 2. 카테고리 업데이트
        await cls._update_category(product, product_update_dto.category_id)

        # 3. 옵션 업데이트
        updated_options = await cls._update_options(product, product_update_dto.options)

        # 4. 재고 업데이트
        await cls._update_stock(product, product_update_dto.options)

        # 5. 이미지 검증 추가
        await cls._validate_images(files, product_update_dto.image_mapping)

        # 6. 이미지 업데이트
        await cls._update_images(
            product,
            updated_options["created"] + updated_options["updated"],
            product_update_dto.image_mapping,
            files,
        )

    @classmethod
    async def delete_product(cls, product_id: int) -> None:
        async with in_transaction() as connection:
            product = await Product.get(id=product_id)

            product_images = await OptionImage.filter(option__product=product).all()

            await cls._delete_images(product_images)

            await product.delete()

    @classmethod
    async def _delete_images(cls, images: list[OptionImage]) -> None:
        if not images:
            return

        object_storage_client = get_object_storage_client()
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        delete_tasks: list[Coroutine[Any, Any, Union[bool, None]]] = []

        for img in images:
            object_name = img.image_url.split(f"{bucket_name}/")[-1]

            delete_tasks.append(object_storage_client.delete_file(bucket_name, object_name))
            delete_tasks.append(img.delete())

        await asyncio.gather(*delete_tasks)
