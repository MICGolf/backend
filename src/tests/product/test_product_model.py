from tortoise.contrib.test import TestCase

from app.product.models.product import CountProduct, DiscountOption, Option, OptionImage, Product


class TestProductModels(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()  # ORM 초기화
        self.product = await Product.create(
            name="Test Product",
            price=100.00,
            discount=10.00,
            discount_option=DiscountOption.PERCENT,
            origin_price=110.00,
            description="Test product description",
            detail="Test product details",
            brand="micgolf",
            status="Y",
            product_code="TEST12345",
        )
        # Option 1 생성
        self.option1 = await Option.create(size="M", color="Red", color_code="#FF0000", product=self.product)
        await CountProduct.create(product=self.product, option=self.option1, count=10)
        await OptionImage.create(image_url="http://example.com/image1.jpg", option=self.option1)

        # Option 2 생성
        self.option2 = await Option.create(size="L", color="Blue", color_code="#0000FF", product=self.product)
        await CountProduct.create(product=self.product, option=self.option2, count=20)
        await OptionImage.create(image_url="http://example.com/image2.jpg", option=self.option2)

    async def test_get_by_id(self) -> None:
        product = await Product.get_by_id(self.product.id)
        assert product.name == "Test Product"
        assert product.price == 100.00

    async def test_get_with_stock_and_images_by_product_id(self) -> None:
        options = await Option.get_with_stock_and_images_by_product_id(self.product.id)

        # 옵션의 개수 확인
        assert len(options) == 2

        # option1에 대한 데이터 검증
        option1 = next(opt for opt in options if opt.size == "M")
        assert option1.stock == 10  # type: ignore[attr-defined]
        assert option1.color == "Red"

        # option2에 대한 데이터 검증
        option2 = next(opt for opt in options if opt.size == "L")
        assert option2.stock == 20  # type: ignore[attr-defined]
        assert option2.color == "Blue"

    async def test_get_all_with_stock_and_images(self) -> None:
        options = await Option.get_all_with_stock_and_images()
        assert len(options) >= 2
        assert options[0].stock == 10  # type: ignore[attr-defined]
        assert options[1].stock == 20  # type: ignore[attr-defined]

    async def test_get_by_product_ids(self) -> None:
        options = await Option.get_by_product_ids([self.product.id])
        assert len(options) == 2
        assert options[0].size == "L"
        assert options[1].size == "M"

    async def test_option_images(self) -> None:
        images = await OptionImage.filter(option=self.option1).all()
        assert len(images) == 1
        assert images[0].image_url == "http://example.com/image1.jpg"

    async def test_count_product(self) -> None:
        count1 = await CountProduct.filter(product=self.product, option=self.option1).first()
        count2 = await CountProduct.filter(product=self.product, option=self.option2).first()

        assert count1 is not None, "CountProduct for option1 was not found"
        assert count2 is not None, "CountProduct for option2 was not found"

        assert count1.count == 10
        assert count2.count == 20
