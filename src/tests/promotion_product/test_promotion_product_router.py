import json

from httpx import AsyncClient
from tortoise.contrib.test import TestCase

from app.product.models.product import DiscountOption, Option, OptionImage, Product
from app.promotion_product.models.promotion_product import PromotionProduct, PromotionType
from main import app


class TestPromotionProductRouterWithExistingPromotion(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        # product, promotion 생성 (프로모션이 있는 경우)
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
            product=self.product,
            promotion_type=PromotionType.MD_PICK.value,
            is_active=True,
        )
        # Option과 OptionImage 생성
        self.option = await Option.create(
            size="Large",
            color="Red",
            color_code="#FF0000",
            product=self.product,
        )

        self.option_image = await OptionImage.create(
            image_url="http://example.com/test_image.jpg",
            option=self.option,
        )

    async def test_get_promotion_products(self) -> None:
        # Given
        promotion_type = self.promotion.promotion_type.value
        page = 1
        size = 10
        url = "/api/v1/promotion-products/get-list"

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url=url,
                params={"page": page, "size": size, "promotion_type": promotion_type},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then
        assert response.status_code == 200
        assert data["items"][0]["product_code"] == self.product.product_code
        assert data["items"][0]["product_name"] == self.product.name
        assert data["items"][0]["price"] == self.product.price
        assert data["items"][0]["is_active"] == self.promotion.is_active
        assert data["items"][0]["promotion_type"] == self.promotion.promotion_type
        assert data["items"][0]["image_url"] == self.option_image.image_url

    async def test_add_existing_promotion_product(self) -> None:
        # Given
        url = "/api/v1/promotion-products/add"
        body = {
            "promotion_type": "md_pick",
            "is_active": True,
            "product_code": self.product.product_code,
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(url=url, json=body, headers={"Accept": "application/json"})
        data = response.json()

        # Then
        assert response.status_code == 200
        assert data["product_code"] == self.product.product_code
        assert data["product_name"] == self.product.name
        assert data["is_active"] == body["is_active"]
        assert data["promotion_type"] == body["promotion_type"]

    async def test_update_existing_promotion_product(self) -> None:
        # Given
        url = "/api/v1/promotion-products/update"
        body = {
            "product_code": self.product.product_code,
            "promotion_type": self.promotion.promotion_type.value,
            "is_active": self.promotion.is_active,
            "new_promotion_type": "best",
            "new_is_active": False,
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.patch(url=url, json=body, headers={"Accept": "application/json"})
        data = response.json()

        # Then
        assert response.status_code == 200
        assert data["promotion_type"] == body["new_promotion_type"]
        assert data["is_active"] == body["new_is_active"]

    async def test_delete_existing_promotion_product(self) -> None:
        # Given
        url = "/api/v1/promotion-products/delete"
        body = {
            "product_code": self.product.product_code,
            "promotion_type": self.promotion.promotion_type.value,
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.request(
                method="DELETE",
                url=url,
                content=json.dumps(body),  # Request Body를 content로 전달
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

        # Then
        assert response.status_code == 200

    async def test_add_new_promotion_product(self) -> None:
        # Given
        url = "/api/v1/promotion-products/add"
        body = {
            "promotion_type": "best",
            "is_active": True,
            "product_code": self.product.product_code,
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(url=url, json=body, headers={"Accept": "application/json"})
        data = response.json()

        # Then
        assert response.status_code == 200
        assert data["product_code"] == self.product.product_code
        assert data["product_name"] == self.product.name
        assert data["is_active"] == body["is_active"]
        assert data["promotion_type"] == body["promotion_type"]

    async def test_delete_nonexistent_promotion_product(self) -> None:
        # Given
        url = "/api/v1/promotion-products/delete"
        body = {
            "product_code": self.product.product_code,
            "promotion_type": "best",
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.request(
                method="DELETE",
                url=url,
                content=json.dumps(body),  # Request Body를 content로 전달
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        data = response.json()

        # Then
        assert response.status_code == 404
        assert (
            data["data"]
            == f"No PromotionProduct found with product_code={body['product_code']}, promotion_type={body['promotion_type']}"
        )

    async def test_update_nonexistent_promotion_product(self) -> None:
        # Given
        url = "/api/v1/promotion-products/update"
        body = {
            "product_code": self.product.product_code,
            "promotion_type": "best",
            "is_active": True,
            "new_promotion_type": "md_pick",
            "new_is_active": False,
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.patch(url=url, json=body, headers={"Accept": "application/json"})
        data = response.json()

        # Then
        assert response.status_code == 404
        assert data["data"] == f"{body['product_code']}의 {body['promotion_type']}은 등록되어 있지 않은 프로모션입니다."
