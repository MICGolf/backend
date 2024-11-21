from tortoise.contrib.test import TestCase

from app.category.models.category import Category, CategoryProduct
from app.product.dtos.request import OptionDTO, ProductDTO, ProductWithOptionCreateRequestDTO, SizeOptionDTO
from app.product.dtos.response import ProductResponseDTO
from app.product.models.product import CountProduct, Option, OptionImage, Product
from app.product.services.product_service import ProductService


class TestProductService(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

        # 카테고리 생성
        self.category = await Category.create(name="Test Category")

        # 상품 생성
        self.product = await Product.create(
            name="Test Product",
            price=100.0,
            discount=10.0,
            discount_option="percent",
            origin_price=110.0,
            description="A test product",
            detail="Detailed description",
            brand="TestBrand",
            status="Y",
            product_code="TEST123",
        )

        # 옵션 생성
        self.option_1 = await Option.create(product=self.product, size="M", color="Red", color_code="#FF0000")
        self.option_2 = await Option.create(product=self.product, size="L", color="Blue", color_code="#0000FF")

        # 옵션 재고 생성
        await CountProduct.create(product=self.product, option=self.option_1, count=50)
        await CountProduct.create(product=self.product, option=self.option_2, count=20)

        # 옵션 이미지 생성
        await OptionImage.create(option=self.option_1, image_url="/path/to/red_image.jpg")
        await OptionImage.create(option=self.option_2, image_url="/path/to/blue_image.jpg")

    async def test_get_product_with_options(self):
        # When: ProductService.get_product_with_options 호출
        result = await ProductService.get_product_with_options(product_id=self.product.id)

        # Then: 반환값 검증 (DTO 기반)
        assert isinstance(result, ProductResponseDTO)
        assert result.product.name == "Test Product"
        assert result.product.product_code == "TEST123"

        # 옵션 검증
        assert len(result.options) == 2

        # 옵션 1 검증
        option_1_dto = result.options[0]
        assert isinstance(option_1_dto, OptionDTO)
        assert option_1_dto.color == "Red"
        assert option_1_dto.color_code == "#FF0000"
        assert len(option_1_dto.sizes) == 1
        assert option_1_dto.sizes[0].size == "M"
        assert option_1_dto.sizes[0].stock == 50

        # 옵션 이미지 검증
        assert len(option_1_dto.images) == 1
        assert option_1_dto.images[0].image_url == "/path/to/red_image.jpg"

        # 옵션 2 검증
        option_2_dto = result.options[1]
        assert isinstance(option_2_dto, OptionDTO)
        assert option_2_dto.color == "Blue"
        assert option_2_dto.color_code == "#0000FF"
        assert len(option_2_dto.sizes) == 1
        assert option_2_dto.sizes[0].size == "L"
        assert option_2_dto.sizes[0].stock == 20

    async def test_create_product_with_single_option(self):
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
            category_id=self.category.id,
            product=product,
            options=options,
            image_mapping=image_mapping,
        )

        files = []  # 이미지 업로드 파일 리스트

        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto,
            files=files,
            upload_dir="/tmp/test_uploads",
        )

        # Then: 데이터베이스에서 생성된 상품 검증
        created_product = await Product.get(product_code="SINGLE123")
        assert created_product.name == "Single Option Product"

        created_options = await Option.filter(product=created_product).all()
        assert len(created_options) == 2
        assert created_options[0].color == "Red"
        assert created_options[0].color_code == "#FF0000"

        created_counts = await CountProduct.filter(product=created_product).all()
        assert len(created_counts) == 2
        assert created_counts[0].count == 10
        assert created_counts[1].count == 20

    async def test_create_product_with_multiple_options(self):
        # Given: 상품 생성 요청 DTO (옵션이 여러 개인 경우)
        product_data = {
            "name": "Multiple Options Product",
            "price": 300.0,
            "discount": 50.0,
            "discount_option": "amount",
            "origin_price": 350.0,
            "description": "Multiple options product description",
            "detail": "Detailed description",
            "product_code": "MULTI123",
        }

        options_data = [
            {
                "color": "Blue",
                "color_code": "#0000FF",
                "sizes": [{"size": "S", "stock": 10}, {"size": "M", "stock": 15}],
            },
            {
                "color": "Yellow",
                "color_code": "#FFFF00",
                "sizes": [{"size": "L", "stock": 20}, {"size": "XL", "stock": 25}],
            },
        ]

        image_mapping = {
            "#0000FF": ["blue_image_1.jpg", "blue_image_2.jpg"],
            "#FFFF00": ["yellow_image_1.jpg"],
        }
        files = []  # 이미지 업로드 파일 리스트

        product_create_dto = {
            "category_id": self.category.id,
            "product": product_data,
            "options": options_data,
            "image_mapping": image_mapping,
        }

        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto,
            files=files,
            upload_dir="/tmp/test_uploads",
        )

        # Then: 데이터베이스에서 생성된 상품 검증
        created_product = await Product.get(product_code="MULTI123")
        assert created_product.name == "Multiple Options Product"

        created_options = await Option.filter(product=created_product).all()
        assert len(created_options) == 4

        created_counts = await CountProduct.filter(product=created_product).all()
        assert len(created_counts) == 4
        assert created_counts[0].count == 10
        assert created_counts[1].count == 15
        assert created_counts[2].count == 20
        assert created_counts[3].count == 25

        # OptionImage 검증
        created_images = await OptionImage.filter(option__product=created_product).all()
        assert len(created_images) == 3  # Blue 옵션에 2개, Yellow 옵션에 1개 이미지
        assert created_images[0].image_url == "/tmp/test_uploads/blue_image_1.jpg"
        assert created_images[1].image_url == "/tmp/test_uploads/blue_image_2.jpg"
        assert created_images[2].image_url == "/tmp/test_uploads/yellow_image_1.jpg"

        # 옵션 1 검증
        assert created_options[0].color == "Blue"
        assert created_options[0].color_code == "#0000FF"
        assert created_options[0].size == "S"

        # 옵션 2 검증
        assert created_options[1].color == "Blue"
        assert created_options[1].color_code == "#0000FF"
        assert created_options[1].size == "M"

        # 옵션 3 검증
        assert created_options[2].color == "Yellow"
        assert created_options[2].color_code == "#FFFF00"
        assert created_options[2].size == "L"

        assert created_product.name == "Multiple Options Product"
        assert created_product.price == 300.0
        assert created_product.discount == 50.0
        assert created_product.discount_option == "amount"
        assert created_product.origin_price == 350.0
        assert created_product.description == "Multiple options product description"
        assert created_product.detail == "Detailed description"
        assert created_product.product_code == "MULTI123"

        # 재고 검증
        assert created_counts[0].option.size == "S"
        assert created_counts[0].count == 10

        assert created_counts[1].option.size == "M"
        assert created_counts[1].count == 15

        assert created_counts[2].option.size == "L"
        assert created_counts[2].count == 20

        assert created_counts[3].option.size == "XL"
        assert created_counts[3].count == 25

    async def test_delete_product(self):
        # When: ProductService.delete_product 호출
        await ProductService.delete_product(product_id=self.product.id)

        # Then: 상품과 관련 데이터가 삭제되었는지 확인
        deleted_product = await Product.filter(id=self.product.id).first()
        assert deleted_product is None

        related_options = await Option.filter(product=self.product)
        assert len(related_options) == 0

        related_count_products = await CountProduct.filter(product=self.product)
        assert len(related_count_products) == 0

        related_images = await OptionImage.filter(option__product=self.product)
        assert len(related_images) == 0
