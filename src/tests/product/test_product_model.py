from tortoise.contrib.test import TestCase

from app.product.models.product import CountProduct, DiscountOption, Option, OptionImage, Product


class TestProductModels(TestCase):
    async def asyncSetUp(self):
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
        self.option1 = await Option.create(size="M", color="Red", color_code="#FF0000", product=self.product)
        self.option2 = await Option.create(size="L", color="Blue", color_code="#0000FF", product=self.product)
        await CountProduct.create(product=self.product, option=self.option1, count=10)
        await CountProduct.create(product=self.product, option=self.option2, count=20)
        await OptionImage.create(image_url="http://example.com/image1.jpg", option=self.option1)
        await OptionImage.create(image_url="http://example.com/image2.jpg", option=self.option2)

    async def test_get_by_id(self):
        product = await Product.get_by_id(self.product.id)
        assert product.name == "Test Product"
        assert product.price == 100.00

    async def test_get_with_stock_and_images_by_product_id(self):
        options = await Option.get_with_stock_and_images_by_product_id(self.product.id)
        assert len(options) == 2
        assert options[0].stock == 10
        assert options[1].stock == 20

    async def test_get_all_with_stock_and_images(self):
        options = await Option.get_all_with_stock_and_images()
        assert len(options) >= 2
        assert options[0].stock == 10
        assert options[1].stock == 20

    async def test_get_by_product_ids(self):
        options = await Option.get_by_product_ids([self.product.id])
        assert len(options) == 2
        assert options[0].size == "M"
        assert options[1].size == "L"

    async def test_option_images(self):
        images = await OptionImage.filter(option=self.option1).all()
        assert len(images) == 1
        assert images[0].image_url == "http://example.com/image1.jpg"

    async def test_count_product(self):
        count1 = await CountProduct.filter(product=self.product, option=self.option1).first()
        count2 = await CountProduct.filter(product=self.product, option=self.option2).first()
        assert count1.count == 10
        assert count2.count == 20