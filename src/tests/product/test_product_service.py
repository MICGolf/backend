from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional, TypedDict
from unittest.mock import AsyncMock, patch

from fastapi import UploadFile
from pydantic import ValidationError
from starlette.datastructures import Headers
from tortoise.contrib.test import TestCase

from app.category.models.category import Category, CategoryProduct
from app.product.dtos.request import (
    BatchUpdateStatusRequest,
    OptionDTO,
    OptionUpdateDTO,
    ProductDTO,
    ProductFilterRequestDTO,
    ProductUpdateDTO,
    ProductWithOptionCreateRequestDTO,
    ProductWithOptionUpdateRequestDTO,
    SizeOptionDTO,
    SizeOptionUpdateDTO,
)
from app.product.dtos.response import ProductResponseDTO
from app.product.models.product import CountProduct, Option, OptionImage, Product
from app.product.services.product_service import ProductService
from common.exceptions.custom_exceptions import MaxImageSizeExceeded, MaxImagesPerColorExceeded


class TestProductService(TestCase):

    @patch("common.utils.object_storage.ObjectStorageClient._upload")
    async def asyncSetUp(self, _: AsyncMock) -> None:
        await super().asyncSetUp()

        self.category_1 = await Category.create(name="Test Category")
        self.category_2 = await Category.create(name="Test Category2")

        # 첫 번째 상품 생성
        product_create_dto_1 = ProductWithOptionCreateRequestDTO(
            category_id=self.category_1.id,
            product=ProductDTO(
                name="Test Product 1",
                price=90000,
                discount=10.0,
                discount_option="percent",
                origin_price=100000,
                description="A test setup product 1",
                detail="Detailed description 1",
                product_code="TEST-PRODUCT-1",
            ),
            options=[
                OptionDTO(
                    color="Red",
                    color_code="#FF0000",
                    sizes=[SizeOptionDTO(size="M", stock=50)],
                ),
                OptionDTO(
                    color="Blue",
                    color_code="#0000FF",
                    sizes=[SizeOptionDTO(size="L", stock=20)],
                ),
            ],
            image_mapping={
                "#FF0000": ["red_image_1.jpg"],
                "#0000FF": ["blue_image_1.jpg"],
            },
        )

        files_1 = [
            UploadFile(
                filename="red_image_1.jpg",
                file=BytesIO(b"mock red image content"),
                headers=Headers({"Content-Type": "image/jpeg"}),
            ),
            UploadFile(
                filename="blue_image_1.jpg",
                file=BytesIO(b"mock blue image content"),
                headers=Headers({"Content-Type": "image/jpeg"}),
            ),
        ]

        # 두 번째 상품 생성
        product_create_dto_2 = ProductWithOptionCreateRequestDTO(
            category_id=self.category_1.id,
            product=ProductDTO(
                name="Test Product 2",
                price=120000,
                discount=15.0,
                discount_option="percent",
                origin_price=140000,
                description="A test setup product 2",
                detail="Detailed description 2",
                product_code="TEST-PRODUCT-2",
            ),
            options=[
                OptionDTO(
                    color="Green",
                    color_code="#00FF00",
                    sizes=[SizeOptionDTO(size="S", stock=30)],
                ),
                OptionDTO(
                    color="Yellow",
                    color_code="#FFFF00",
                    sizes=[SizeOptionDTO(size="XL", stock=10)],
                ),
            ],
            image_mapping={
                "#00FF00": ["green_image.jpg"],
                "#FFFF00": ["yellow_image.jpg"],
            },
        )

        files_2 = [
            UploadFile(
                filename="green_image.jpg",
                file=BytesIO(b"mock green image content"),
                headers=Headers({"Content-Type": "image/jpeg"}),
            ),
            UploadFile(
                filename="yellow_image.jpg",
                file=BytesIO(b"mock yellow image content"),
                headers=Headers({"Content-Type": "image/jpeg"}),
            ),
        ]

        # 세 번째 상품 생성
        product_create_dto_3 = ProductWithOptionCreateRequestDTO(
            category_id=self.category_2.id,
            product=ProductDTO(
                name="Test Product 3",
                price=50000,
                discount=5.0,
                discount_option="amount",
                origin_price=55000,
                description="A test setup product 3",
                detail="Detailed description 3",
                product_code="TEST-PRODUCT-3",
            ),
            options=[
                OptionDTO(
                    color="Green",
                    color_code="#00FF00",
                    sizes=[SizeOptionDTO(size="S", stock=10)],
                ),
            ],
            image_mapping={
                "#00FF00": ["green_image.jpg"],
            },
        )

        files_3 = [
            UploadFile(
                filename="green_image.jpg",
                file=BytesIO(b"mock green image content"),
                headers=Headers({"Content-Type": "image/jpeg"}),
            ),
        ]

        # 서비스 호출
        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto_1,
            files=files_1,
        )

        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto_2,
            files=files_2,
        )
        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto_3,
            files=files_3,
        )

        # 상품 조회
        self.product_1 = await Product.get(product_code="TEST-PRODUCT-1")
        self.product_2 = await Product.get(product_code="TEST-PRODUCT-2")
        self.product_3 = await Product.get(product_code="TEST-PRODUCT-3")

        # 4번쨰 상품 생성 및 조회
        self.product_4 = await Product.create(
            name="Test Product 4",
            price=50000,
            discount=5.0,
            discount_option="amount",
            origin_price=55000,
            description="A test setup product 4",
            detail="Detailed description 4",
            product_code="TEST-PRODUCT-4",
            status="N",
        )

        # 옵션 조회
        self.options_1 = await Option.filter(product=self.product_1).all()
        self.options_2 = await Option.filter(product=self.product_2).all()
        self.options_3 = await Option.filter(product=self.product_3).all()

        # 재고 및 이미지 조회
        # 재고와 관련된 옵션 데이터를 미리 로드
        self.count_products_1 = await CountProduct.filter(product=self.product_1).prefetch_related("option").all()
        self.count_products_2 = await CountProduct.filter(product=self.product_2).prefetch_related("option").all()
        self.count_products_3 = await CountProduct.filter(product=self.product_3).prefetch_related("option").all()

        self.option_images_1 = await OptionImage.filter(option__product=self.product_1).select_related("option").all()
        self.option_images_2 = await OptionImage.filter(option__product=self.product_2).select_related("option").all()
        self.option_images_3 = await OptionImage.filter(option__product=self.product_3).select_related("option").all()

    @staticmethod
    def create_mock_file(filename: str, content_type: str, content: bytes) -> UploadFile:
        return UploadFile(
            filename=filename,
            file=BytesIO(content),
            headers=Headers({"Content-Type": content_type}),
        )

    async def test_상품_단건_조회(self) -> None:
        # When: 단건 조회 호출
        response = await ProductService.get_product_with_options(product_id=self.product_1.id)

        # Then: 상품 정보 검증
        assert isinstance(response, ProductResponseDTO)
        assert response.product.name == self.product_1.name
        assert response.product.price == self.product_1.price
        assert response.product.discount == self.product_1.discount
        assert response.product.product_code == self.product_1.product_code

        # 옵션 검증
        assert len(response.options) == len(self.options_1)

        for response_option in response.options:
            db_option = next((opt for opt in self.options_1 if opt.color == response_option.color), None)
            assert db_option is not None
            assert response_option.color_code == db_option.color_code

            db_images = [img.image_url for img in self.option_images_1 if img.option.id == db_option.id]
            response_images = [img.image_url for img in response_option.images]
            assert set(db_images) == set(response_images)

            stock_map = {(cp.option.color, cp.option.size): cp.count for cp in self.count_products_1}
            response_stocks = {(sz.size, response_option.color): sz.stock for sz in response_option.sizes}

            for (size, color), stock in response_stocks.items():
                assert (color, size) in stock_map
                expected_stock = stock_map[(color, size)]
                assert stock == expected_stock

    async def test_dto_유효한_날짜_검증(self) -> None:
        # Given
        class ProductFilterData(TypedDict, total=False):
            product_name: Optional[str]
            product_id: Optional[int]
            product_code: Optional[str]
            sale_status: Optional[str]
            category_id: Optional[int]
            start_date: Optional[datetime]
            end_date: Optional[datetime]

        data: ProductFilterData = {
            "product_name": "Invalid Date Test",
            "start_date": datetime(2023, 1, 31),
            "end_date": datetime(2023, 12, 1),
        }

        # When
        dto = ProductFilterRequestDTO(**data)

        # Then
        self.assertEqual(dto.product_name, "Invalid Date Test")

    async def test_dto_유효하지_않은_날짜_검증(self) -> None:
        class ProductFilterData(TypedDict, total=False):
            product_name: Optional[str]
            product_id: Optional[int]
            product_code: Optional[str]
            sale_status: Optional[str]
            category_id: Optional[int]
            start_date: Optional[datetime]
            end_date: Optional[datetime]

        data: ProductFilterData = {
            "product_name": "Invalid Date Test",
            "start_date": datetime(2023, 12, 31),
            "end_date": datetime(2023, 1, 1),
        }

        # When / Then
        with self.assertRaises(ValidationError) as context:
            ProductFilterRequestDTO(**data)

        self.assertIn("start_date는 end_date보다 빠를 수 없습니다.", str(context.exception))

    async def test_상품_조회_상품명으로_검색(self) -> None:
        # When
        response = await ProductService.get_products_with_options(product_name="Test Product 1")

        # Then
        assert len(response) == 1
        assert response[0].product.name == "Test Product 1"
        assert response[0].product.id == self.product_1.id

    async def test_상품_조회_상품ID로_검색(self) -> None:
        # When
        response = await ProductService._get_filtered_products_and_options(product_id=self.product_2.id)

        # Then
        products, _ = response
        assert len(products) == 1
        assert products[0].id == self.product_2.id

    async def test_상품_조회_상품코드로_검색(self) -> None:
        # When
        response = await ProductService.get_products_with_options(product_code="TEST-PRODUCT-3")

        # Then
        assert len(response) == 1
        assert response[0].product.product_code == "TEST-PRODUCT-3"

    async def test_상품_조회_판매상태로_검색_Y(self) -> None:
        # When
        response = await ProductService.get_products_with_options(sale_status="Y")

        # Then
        assert len(response) == 3  # 모든 상품이 "Y" 상태로 설정됨
        product_ids = [res.product.id for res in response]
        assert self.product_1.id in product_ids
        assert self.product_2.id in product_ids

    async def test_상품_조회_판매상태로_검색_N(self) -> None:
        # When
        response = await ProductService.get_products_with_options(sale_status="N")

        # Then
        assert len(response) == 1
        assert response[0].product.product_code == "TEST-PRODUCT-4"

    async def test_상품_조회_카테고리ID로_검색(self) -> None:
        # When
        response = await ProductService.get_products_with_options(category_id=self.category_1.id)

        # Then
        products = [self.product_1.product_code, self.product_2.product_code]

        # 검증
        assert len(response) == 2  # 모든 상품이 동일한 카테고리에 속함
        assert response[0].product.product_code in products
        assert response[1].product.product_code in products

    async def test_상품_조회_생성일로_검색(self) -> None:
        # When
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        response = await ProductService.get_products_with_options(start_date=start_date, end_date=end_date)

        # Then
        assert len(response) == 4  # 모두 해당 날짜 범위에 생성됨

    async def test_상품_조회_상품명과_판매상태_조합(self) -> None:
        # When
        response = await ProductService.get_products_with_options(
            product_name="Test Product 1",
            sale_status="Y",
        )

        # Then
        assert len(response) == 1
        assert response[0].product.name == "Test Product 1"
        assert response[0].product.status == "Y"

    async def test_상품_조회_카테고리와_날짜_조합(self) -> None:
        # When
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        response = await ProductService.get_products_with_options(
            category_id=self.category_1.id,
            start_date=start_date,
            end_date=end_date,
        )

        # Then
        assert len(response) == 2  # 모든 상품이 동일한 카테고리 및 날짜 범위에 해당

    async def test_상품_조회_상품코드와_판매상태_조합(self) -> None:
        # When
        response = await ProductService.get_products_with_options(
            product_code="TEST-PRODUCT-2",
            sale_status="Y",
        )

        # Then
        assert len(response) == 1
        assert response[0].product.product_code == "TEST-PRODUCT-2"
        assert response[0].product.status == "Y"

    async def test_상품_조회_상품명과_시작일_조합(self) -> None:
        # When
        start_date = datetime.now() - timedelta(days=1)
        response = await ProductService.get_products_with_options(
            product_name="Test Product 3",
            start_date=start_date,
        )

        # Then
        assert len(response) == 1
        assert response[0].product.name == "Test Product 3"

    async def test_상품_조회_카테고리와_상품명과_종료일_조합(self) -> None:
        # When
        end_date = datetime.now() + timedelta(days=1)
        response = await ProductService.get_products_with_options(
            category_id=self.category_1.id,
            product_name="Test Product 2",
            end_date=end_date,
        )

        # Then
        assert len(response) == 1
        assert response[0].product.name == "Test Product 2"

    async def test_상품_조회_상품ID와_날짜_조합(self) -> None:
        # When
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        response = await ProductService.get_products_with_options(
            product_id=self.product_1.id,
            start_date=start_date,
            end_date=end_date,
        )

        # Then
        assert len(response) == 1
        assert response[0].product.id == self.product_1.id

    async def test_상품_조회_판매상태와_날짜_조합(self) -> None:
        # When
        start_date = datetime.now() - timedelta(days=10)
        end_date = datetime.now()
        response = await ProductService.get_products_with_options(
            sale_status="Y",
            start_date=start_date,
            end_date=end_date,
        )

        # Then
        assert len(response) > 0
        for response_product in response:
            assert response_product.product.status == "Y"

    async def test_상품_조회_조건_불일치(self) -> None:
        # When
        response = await ProductService.get_products_with_options(
            product_name="Non-existent Product",
            sale_status="N",
        )

        # Then
        assert len(response) == 0

    async def test_상품_조회_페이지와_페이지크기(self) -> None:
        # When
        response = await ProductService.get_products_with_options(
            page=1,
            page_size=2,
        )

        # Then
        assert len(response) == 2  # 페이지 크기만큼 반환
        assert response[0].product.name == "Test Product 4"
        assert response[1].product.name == "Test Product 3"

    async def test_상품_조회_가격기준_정렬_오름차순(self) -> None:
        # When
        response = await ProductService.get_products_with_options(
            sort="price",
            order="asc",
        )

        # Then
        assert len(response) > 0
        prices = [product.product.price for product in response]
        assert prices == sorted(prices)

    async def test_상품_조회_가격기준_정렬_내림차순(self) -> None:
        # When
        response = await ProductService.get_products_with_options(
            sort="price",
            order="desc",
        )

        # Then
        assert len(response) > 0
        prices = [product.product.price for product in response]
        assert prices == sorted(prices, reverse=True), "상품이 가격 내림차순으로 정렬되지 않았습니다."

    async def test_상품_조회_페이지와_정렬_조합(self) -> None:
        # When
        response = await ProductService.get_products_with_options(
            page=1,
            page_size=4,
            sort="created_at",
            order="asc",
        )

        # Then
        assert len(response) == 4
        created_dates = [product.product.id for product in response]
        assert created_dates == sorted(created_dates)

    async def test_상품_조회_페이지크기_범위초과(self) -> None:
        # When
        response = await ProductService.get_products_with_options(
            page=3,
            page_size=2,
        )

        # Then
        assert len(response) == 0

    async def test_상품_조회_기본정렬(self) -> None:
        # When
        response = await ProductService.get_products_with_options()

        # Then
        assert len(response) > 0
        created_dates = [product.product.id for product in response]
        assert created_dates == sorted(created_dates, reverse=True)

    async def test_상품_조회_조건없음(self) -> None:
        # When
        response = await ProductService.get_products_with_options()
        # Then
        assert len(response) == 4

    async def test_상품_생성_요청_옵션_1개(self) -> None:
        # Given: 상품 생성 요청 DTO (옵션이 1개인 경우)
        product = ProductDTO(
            name="Single Option Product",
            price=200.0,
            discount=20.0,
            discount_option="percent",
            origin_price=250.0,
            description="This is a test product",
            detail="Detailed description of the test product",
            product_code="SINGLE123",
        )
        options = [
            OptionDTO(
                color="Red",
                color_code="#FF0000",
                sizes=[SizeOptionDTO(size="S", stock=10), SizeOptionDTO(size="M", stock=20)],
            ),
        ]
        image_mapping = {"#FF0000": ["red_image1.jpg", "red_image2.jpg"]}

        product_create_dto = ProductWithOptionCreateRequestDTO(
            category_id=self.category_1.id,
            product=product,
            options=options,
            image_mapping=image_mapping,
        )

        files: list[UploadFile] = []  # 이미지 업로드 파일 리스트

        # When: 상품 생성 서비스 호출
        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto,
            files=files,
        )

        # Then: 상품 검증
        created_product = await Product.get(product_code="SINGLE123")
        assert created_product.name == "Single Option Product"
        assert created_product.price == 200.0
        assert created_product.discount == 20.0

        # 옵션 검증
        created_options = await Option.filter(product=created_product).all()
        assert len(created_options) == 2, "Expected 2 options to be created (2 sizes for 1 color)"
        assert all(option.color == "Red" for option in created_options)
        assert all(option.color_code == "#FF0000" for option in created_options)

        sizes = {option.size for option in created_options}
        assert sizes == {"S", "M"}, f"Expected sizes {{'S', 'M'}}, but got {sizes}"

        # 재고 검증
        created_counts = await CountProduct.filter(product=created_product).prefetch_related("option").all()
        stock_map = {("Red", "S"): 10, ("Red", "M"): 20}
        assert len(created_counts) == 2, "Expected 2 stock entries for the options"

        for count in created_counts:
            key = (count.option.color, count.option.size)
            assert key in stock_map, f"Unexpected stock key {key}"
            expected_stock = stock_map[key]
            assert count.count == expected_stock, f"Expected stock {expected_stock} for {key}, but got {count.count}"

        # 이미지 검증
        option_images = await OptionImage.filter(option__product=created_product).all()
        assert len(option_images) == 0, "Expected no option images as no files were uploaded"

    @patch("common.utils.object_storage.ObjectStorageClient._upload")
    async def test_상품_생성_요청_옵션_여러_개(self, _: AsyncMock) -> None:
        # Given: 상품 생성 요청 DTO
        product = ProductDTO(
            name="Multi Option Product",
            price=300.0,
            discount=10.0,
            discount_option="percent",
            origin_price=330.0,
            description="This is a test product with multiple options",
            detail="Detailed description of the test product with multiple options",
            product_code="MULTI123",
        )
        options = [
            OptionDTO(
                color="Red",
                color_code="#FF0000",
                sizes=[SizeOptionDTO(size="S", stock=10), SizeOptionDTO(size="M", stock=20)],
            ),
            OptionDTO(
                color="Blue",
                color_code="#0000FF",
                sizes=[SizeOptionDTO(size="L", stock=15), SizeOptionDTO(size="XL", stock=5)],
            ),
            OptionDTO(
                color="Green",
                color_code="#00FF00",
                sizes=[SizeOptionDTO(size="M", stock=25), SizeOptionDTO(size="L", stock=10)],
            ),
        ]
        image_mapping = {
            "#FF0000": ["red_image1.jpg", "red_image2.jpg"],
            "#0000FF": ["blue_image1.jpg", "blue_image2.jpg"],
            "#00FF00": ["green_image1.jpg", "green_image2.jpg"],
        }

        product_create_dto = ProductWithOptionCreateRequestDTO(
            category_id=self.category_1.id,
            product=product,
            options=options,
            image_mapping=image_mapping,
        )

        files = [
            "red_image1.jpg",
            "red_image2.jpg",
            "blue_image1.jpg",
            "blue_image2.jpg",
            "green_image1.jpg",
            "green_image2.jpg",
        ]

        mock_files = [
            UploadFile(
                filename=file_name,
                file=BytesIO(b"mock file content"),
                headers=Headers({"Content-Type": "image/jpeg"}),
            )
            for file_name in files
        ]

        # When: 상품 생성 서비스 호출
        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto,
            files=mock_files,
        )

        # Then: 상품 검증
        created_product = await Product.get(product_code="MULTI123")
        assert created_product.name == "Multi Option Product"
        assert created_product.price == 300.0
        assert created_product.discount == 10.0

        # 옵션 검증
        created_options = await Option.filter(product=created_product).all()
        assert len(created_options) == 6, "Expected 6 options to be created"

        # 재고 검증
        created_counts = await CountProduct.filter(product=created_product).prefetch_related("option").all()
        stock_map = {
            ("Red", "S"): 10,
            ("Red", "M"): 20,
            ("Blue", "L"): 15,
            ("Blue", "XL"): 5,
            ("Green", "M"): 25,
            ("Green", "L"): 10,
        }

        for count in created_counts:
            key = (count.option.color, count.option.size)
            assert key in stock_map, f"Unexpected stock key {key}"

            expected_stock = stock_map[key]
            assert count.count == expected_stock, f"Expected stock {expected_stock} but got {count.count} for {key}"

        # 이미지 검증
        option_images = await OptionImage.filter(option__product=created_product).prefetch_related("option").all()
        image_map = {
            "#FF0000": ["red_image1.jpg", "red_image2.jpg"],
            "#0000FF": ["blue_image1.jpg", "blue_image2.jpg"],
            "#00FF00": ["green_image1.jpg", "green_image2.jpg"],
        }

        for option in created_options:
            assert option.color_code in image_map
            expected_images = image_map[option.color_code]

            option_images_for_option = [img for img in option_images if img.option_id == option.id]  # type: ignore

            extracted_image_names = [img.image_url.split("/")[-1].split("_", 1)[-1] for img in option_images_for_option]

            assert set(extracted_image_names) == set(
                expected_images
            ), f"Expected images {expected_images} but got {extracted_image_names}"

    @patch("common.utils.object_storage.ObjectStorageClient._upload")
    async def test_상품_수정_요청_옵션_여러_개(self, _: AsyncMock) -> None:

        product_id = self.product_1.id

        product_update_dto = ProductWithOptionUpdateRequestDTO(
            category_id=self.category_2.id,
            product=ProductUpdateDTO(
                name="Updated Test Product 1",
                price=95000,
                discount=15.0,
                discount_option="amount",
                origin_price=110000,
                description="Updated description",
                detail="Updated detail",
                product_code="TEST-PRODUCT-1",
            ),
            options=[
                OptionUpdateDTO(
                    id=self.options_1[0].id,  # 기존 옵션 업데이트 (Red)
                    color="Red",
                    color_code="#FF0000",
                    sizes=[
                        SizeOptionUpdateDTO(id=self.count_products_1[0].id, size="M", stock=60),
                        SizeOptionUpdateDTO(size="L", stock=30),  # 새로운 사이즈 추가
                    ],
                ),
                OptionUpdateDTO(
                    color="Green",  # 새로운 옵션 추가
                    color_code="#00FF00",
                    sizes=[SizeOptionUpdateDTO(size="S", stock=15)],
                ),
            ],
            image_mapping={
                "#FF0000": ["red_image_updated.jpg"],
                "#00FF00": ["green_image_new.jpg"],
            },
        )

        files = [
            UploadFile(
                filename="red_image_updated.jpg",
                file=BytesIO(b"mock red image content"),
                headers=Headers({"Content-Type": "image/jpeg"}),
            ),
            UploadFile(
                filename="green_image_new.jpg",
                file=BytesIO(b"mock green image content"),
                headers=Headers({"Content-Type": "image/jpeg"}),
            ),
        ]

        # When: 상품 업데이트 호출
        await ProductService.update_product_with_options(
            product_id=product_id, product_update_dto=product_update_dto, files=files
        )

        # Then: 상품 기본 정보 검증
        updated_product = await Product.get(id=product_id).prefetch_related("product_category__category")
        assert updated_product.name == "Updated Test Product 1"
        assert updated_product.price == 95000
        assert updated_product.discount == 15.0

        # 카테고리 검증
        related_categories = await Category.filter(category_product__product=updated_product).all()
        assert len(related_categories) == 1, "관련된 카테고리는 하나여야 합니다."
        assert related_categories[0].id == self.category_2.id, "카테고리가 올바르게 업데이트되지 않았습니다."

        # Then: 옵션 업데이트 검증
        updated_options = await Option.filter(product=updated_product).all()
        assert len(updated_options) == 3, "총 옵션이 3개여야 합니다."

        # 기존 옵션 업데이트 검증
        red_option = next(opt for opt in updated_options if opt.color_code == "#FF0000")
        assert red_option.color == "Red"

        # 새 옵션 추가 검증
        green_option = next(opt for opt in updated_options if opt.color_code == "#00FF00")
        assert green_option.color == "Green"

        # Then: 재고 업데이트 검증
        updated_counts = await CountProduct.filter(product=updated_product).prefetch_related("option").all()
        stock_map = {
            ("#FF0000", "M"): 60,
            ("#FF0000", "L"): 30,
            ("#00FF00", "S"): 15,
        }
        for count in updated_counts:
            key = (count.option.color_code, count.option.size)
            assert stock_map[key] == count.count, f"Expected {stock_map[key]} but got {count.count}"

        # Then: 이미지 업데이트 검증
        updated_images = await OptionImage.filter(option__product=updated_product).prefetch_related("option").all()
        image_map = {
            "#FF0000": ["red_image_updated.jpg"],
            "#00FF00": ["green_image_new.jpg"],
        }

        for option in updated_options:
            assert (
                option.color_code in image_map
            ), f"Option with color code {option.color_code} not in expected image map."
            expected_images = image_map[option.color_code]

            option_images_for_option = [img for img in updated_images if img.option.id == option.id]

            extracted_image_names = [img.image_url.split("/")[-1].split("_", 1)[-1] for img in option_images_for_option]

            print(f"Extracted images for option {option.color_code}: {extracted_image_names}")
            print(f"Expected images for option {option.color_code}: {expected_images}")

            assert set(extracted_image_names) == set(
                expected_images
            ), f"Expected images {expected_images} but got {extracted_image_names} for option {option.color_code}."

    @patch("common.utils.object_storage.ObjectStorageClient.delete_file")
    async def test_단일_상품_삭제(self, _: AsyncMock) -> None:
        # Given: 삭제할 상품 준비
        product_id = self.product_1.id

        # When: 상품 삭제 호출
        await ProductService.delete_product(product_id)

        # Then: 상품 삭제 확인
        deleted_product = await Product.filter(id=product_id).first()
        assert deleted_product is None, f"상품 {product_id}가 삭제되지 않았습니다."

        # Then: 관련된 이미지가 삭제되었는지 확인
        remaining_images = await OptionImage.filter(option__product=self.product_1).all()
        assert len(remaining_images) == 0, f"상품 {product_id}의 이미지가 삭제되지 않았습니다."

    async def test_유효한_이미지(self) -> None:
        files = [
            self.create_mock_file("red_image_1.jpg", "image/jpeg", b"mock red image content"),
            self.create_mock_file("blue_image_1.jpg", "image/jpeg", b"mock blue image content"),
        ]

        image_mapping = {"#FF0000": ["red_image_1.jpg"], "#0000FF": ["blue_image_1.jpg"]}

        # _validate_images 메서드 호출
        await ProductService._validate_images(files, image_mapping)

    async def test_잘못된_확장자(self) -> None:
        files = [self.create_mock_file("red_image_1.gif", "image/gif", b"mock red image content")]

        image_mapping = {"#FF0000": ["red_image_1.gif"]}

        with self.assertRaises(ValueError) as context:
            await ProductService._validate_images(files, image_mapping)

        self.assertEqual(str(context.exception), "Invalid image type: image/gif. Only JPEG and PNG are allowed.")

    async def test_이미지_7장_초과(self) -> None:
        files = [self.create_mock_file(f"red_image_{i}.jpg", "image/jpeg", b"mock red image content") for i in range(7)]

        image_mapping = {"#FF0000": [f"red_image_{i}.jpg" for i in range(7)]}

        with self.assertRaises(MaxImagesPerColorExceeded) as context:
            await ProductService._validate_images(files, image_mapping)

        self.assertEqual(str(context.exception.color_code), "#FF0000")

    async def test_옵션당_2MB_초과(self) -> None:
        files = [
            self.create_mock_file("red_image_1.jpg", "image/jpeg", b"x" * (2 * 1024 * 1024 + 1)),  # 2MB + 1 byte
        ]

        image_mapping = {"#FF0000": ["red_image_1.jpg"]}

        with self.assertRaises(MaxImageSizeExceeded) as context:
            await ProductService._validate_images(files, image_mapping)

        assert context.exception.max_size < 2 * 1024 * 1024 + 1

    async def test_color_code_불일치(self) -> None:
        files = [self.create_mock_file("red_image_1.jpg", "image/jpeg", b"mock red image content")]

        image_mapping: dict[str, list[str]] = {}

        with self.assertRaises(ValueError) as context:
            await ProductService._validate_images(files, image_mapping)

        self.assertEqual(str(context.exception), f"Image red_image_1.jpg does not have a valid color code mapping.")

    async def test_상품_상태_업데이트(self) -> None:
        # Given
        batch_request = BatchUpdateStatusRequest(product_ids=[1, 2], status="N")

        # When
        await ProductService.update_products_status(batch_request.product_ids, batch_request.status)

        # Then
        updated_products = await Product.filter(id__in=batch_request.product_ids).all()

        for product in updated_products:
            self.assertEqual(product.status, batch_request.status)

    async def test_상품_업데이트_카테고리_동일(self) -> None:
        await ProductService._update_category(product=self.product_1, new_category_id=self.category_1.id)

        category = await Category.get(id=self.category_1.id)

        assert self.category_1.id == category.id
