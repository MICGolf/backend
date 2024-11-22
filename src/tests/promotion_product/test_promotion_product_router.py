from httpx import AsyncClient
from tortoise.contrib.test import TestCase

from app.product.models.product import DiscountOption, Product
from app.promotion_product.models.promotion_product import PromotionProduct, PromotionType
from main import app


class TestPromotionProductRouter(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        # product, promotion 생성
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
        self.promotion = await PromotionProduct.create(
            product=self.product, promotion_type=PromotionType.MD_PICK, is_active=True
        )

    async def test_get_promotion_product(self) -> None:
        # Given
        product = await Product.get(name="Test Product")

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url=f"/api/v1/promotion-products",
                params={"promotion_type": "md_pick", "page": 1, "size": 10},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then
        assert response.status_code == 200
        assert "items" in response.json()
        assert data["items"][0]["product_name"] == product.name

    async def test_get_promotion_products_invalid_type(self) -> None:
        # Given
        product = await Product.get(name="Test Product")

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url=f"/api/v1/promotion-products",
                params={"promotion_type": "invalid_type", "page": 1, "size": 10},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then
        assert response.status_code == 400
        assert data["data"] == "Invalid promotion type. Choose 'best' or 'md_pick'."
