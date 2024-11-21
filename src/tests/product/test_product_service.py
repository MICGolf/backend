from tortoise.contrib.test import TestCase
from app.product.models.product import Product, Option, CountProduct, OptionImage
from app.category.models.category import Category, CategoryProduct
from app.product.dtos.response import ProductResponseDTO, OptionDTO, OptionImageDTO, ProductDTO
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

    async def test_create_product_with_options(self):
        # Given: 상품 생성 요청 DTO
        product_data = {
            "name": "New Product",
            "price": 200.0,
            "discount": 20.0,
            "discount_option": "amount",
            "origin_price": 220.0,
            "description": "New product description",
            "detail": "Detailed description",
            "product_code": "NEW123",
        }

        options_data = [
            {
                "color": "Green",
                "color_code": "#00FF00",
                "sizes": [{"size": "M", "stock": 30}, {"size": "L", "stock": 40}],
            }
        ]

        image_mapping = {"#00FF00": ["green_image_1.jpg", "green_image_2.jpg"]}
        files = []  # 이미지 업로드 파일 리스트

        product_create_dto = {
            "category_id": self.category.id,
            "product": product_data,
            "options": options_data,
            "image_mapping": image_mapping,
        }

        # When: ProductService.create_product_with_options 호출
        await ProductService.create_product_with_options(
            product_create_dto=product_create_dto,
            files=files,
            upload_dir="/tmp/test_uploads",
        )

        # Then: 데이터베이스에서 생성된 상품 검증
        created_product = await Product.get(product_code="NEW123")
        assert created_product.name == "New Product"

        # DTO로 변환하여 응답 시뮬레이션
        created_product_dto = ProductDTO.model_validate(created_product)
        assert created_product_dto.name == "New Product"
        assert created_product_dto.product_code == "NEW123"

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
