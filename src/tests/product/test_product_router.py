from httpx import AsyncClient
from tortoise.contrib.test import TestCase

from app.product.models.product import DiscountOption, Product
from main import app


class TestProductRouter(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()  # ORM 초기화
        self.test_product = await Product.create(
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

    async def test_products(self) -> None:
        # Given: Ensure the test_product is available
        product = await Product.get(product_code="TEST12345")
        assert product.name == "Test Product"

        # When: Make the GET request
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url="/api/v1/products",  # Update the URL if necessary
                headers={"Accept": "application/json"},
            )

        # # Then: Assert the response
        # assert response.status_code == 200
        # data = response.json()
        # assert len(data) > 0
        # assert data[0]["name"] == "Test Product"
