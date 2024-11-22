from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional, TypedDict
from unittest.mock import AsyncMock, patch

from fastapi import UploadFile
from pydantic import ValidationError
from tortoise.contrib.test import TestCase

from app.category.models.category import Category
from app.product.dtos.request import (
    OptionDTO,
    ProductDTO,
    ProductFilterRequestDTO,
    ProductWithOptionCreateRequestDTO,
    SizeOptionDTO,
)
from app.product.dtos.response import ProductResponseDTO
from app.product.models.product import CountProduct, Option, OptionImage, Product
from app.product.services.product_service import ProductService


class TestProductService(TestCase):
    async def asyncSetUp(self) -> None:
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
                "#FF0000": ["/path/to/red_image_1.jpg"],
                "#0000FF": ["/path/to/blue_image_1.jpg"],
            },
        )

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
                "#00FF00": ["/path/to/green_image.jpg"],
                "#FFFF00": ["/path/to/yellow_image.jpg"],
            },
        )

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
                "#00FF00": ["/path/to/green_image.jpg"],
            },
        )

        # 서비스 호출
        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto_1,
            files=[],
        )

        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto_2,
            files=[],
        )
        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto_3,
            files=[],
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

        self.option_images_1 = await OptionImage.filter(option__product=self.product_1).all()
        self.option_images_2 = await OptionImage.filter(option__product=self.product_2).all()
        self.option_images_3 = await OptionImage.filter(option__product=self.product_3).all()

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

        mock_files = [UploadFile(filename=file_name, file=BytesIO(b"mock file content")) for file_name in files]

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

            extracted_image_names = [
                "_".join(image.image_url.split("/")[-1].split("_")[1:]) for image in option_images_for_option
            ]

            assert set(extracted_image_names) == set(
                expected_images
            ), f"Expected images {expected_images} but got {extracted_image_names}"

    # async def test_delete_product(self):
    #     # When: ProductService.delete_product 호출
    #     await ProductService.delete_product(product_id=self.product.id)
    #
    #     # Then: 상품과 관련 데이터가 삭제되었는지 확인
    #     deleted_product = await Product.filter(id=self.product.id).first()
    #     assert deleted_product is None
    #
    #     related_options = await Option.filter(product=self.product)
    #     assert len(related_options) == 0
    #
    #     related_count_products = await CountProduct.filter(product=self.product)
    #     assert len(related_count_products) == 0
    #
    #     related_images = await OptionImage.filter(option__product=self.product)
    #     assert len(related_images) == 0
