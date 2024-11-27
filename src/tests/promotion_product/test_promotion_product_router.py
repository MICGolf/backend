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
            product=self.product, promotion_type=PromotionType.MD_PICK.value, is_active=True
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

    async def test_get_promotion_products_error(self) -> None:
        # Given
        promotion_type = "randomstring"
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
        assert data["code"] == 400
        assert data["data"] == "Invalid promotion type. Choose 'best' or 'md_pick'."

    async def test_add_existing_promotion_product(self) -> None:
        # Given
        promotion_type = "md_pick"
        is_active = True
        product_code = self.product.product_code
        url = "/api/v1/promotion-products/add"

        # When: 이미 존재하는 프로모션을 추가하려고 할 때
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url=url,
                params={"promotion_type": promotion_type, "product_code": product_code, "is_active": is_active},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then: 기존 프로모션이 업데이트되는지 확인
        assert response.status_code == 200
        assert data["product_code"] == product_code
        assert data["product_name"] == self.product.name
        assert data["is_active"] == is_active
        assert data["promotion_type"] == promotion_type

    async def test_add_existing_promotion_product_error(self) -> None:
        # Given: 잘못된 promotion_type 사용
        promotion_type = "invalid_type"
        is_active = True
        product_code = self.product.product_code
        url = "/api/v1/promotion-products/add"

        # When: 잘못된 promotion_type으로 프로모션 추가 시도
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url=url,
                params={"promotion_type": promotion_type, "product_code": product_code, "is_active": is_active},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then: 400 에러와 올바른 오류 메시지 확인
        assert response.status_code == 400
        assert data["data"] == "Invalid promotion type. Choose 'best' or 'md_pick'."

        # Given: is_active가 boolean이 아님
        promotion_type = "md_pick"
        is_active: str = "not_boolean"  # type: ignore

        # When: 잘못된 is_active로 프로모션 추가 시도
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url=url,
                params={"promotion_type": promotion_type, "product_code": product_code, "is_active": is_active},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then: 400 에러와 올바른 오류 메시지 확인
        assert response.status_code == 422
        assert data["message"] == "Validation failed. Please check your input."

        # Given: product_code가 없음
        product_code = ""

        # When: product_code가 없는 상태로 프로모션 추가 시도
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url=url,
                params={"promotion_type": promotion_type, "is_active": True, "product_code": product_code},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then: 400 에러와 올바른 오류 메시지 확인
        assert response.status_code == 400
        assert data["data"] == "Product Code is required."

    async def test_delete_existing_promotion_product(self) -> None:
        # Given
        product_code = self.product.product_code
        promotion_type = self.promotion.promotion_type.value
        url = "/api/v1/promotion-products/delete"

        # When: 기존 프로모션을 삭제할 때
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                url=url,
                params={"product_code": product_code, "promotion_type": promotion_type},
                headers={"Accept": "application/json"},
            )

        # Then: 삭제가 성공적으로 이루어지는지 확인
        assert response.status_code == 200

    async def test_update_existing_promotion_product(self) -> None:
        # Given
        product_code = self.product.product_code
        promotion_type = self.promotion.promotion_type.value
        is_active = self.promotion.is_active
        new_promotion_type = "best"
        new_is_active = False
        url = "/api/v1/promotion-products/update"

        # When: 기존 프로모션을 업데이트할 때
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.patch(
                url=url,
                params={
                    "product_code": product_code,
                    "promotion_type": promotion_type,
                    "is_active": is_active,
                    "new_promotion_type": new_promotion_type,
                    "new_is_active": new_is_active,
                },
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then: 업데이트가 성공적으로 이루어지는지 확인
        assert response.status_code == 200
        assert data["promotion_type"] == new_promotion_type
        assert data["is_active"] == new_is_active


class TestPromotionProductRouterWithoutExistingPromotion(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        # product 생성 (프로모션이 없는 경우)
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
        self.promotion = None

    async def test_add_new_promotion_product(self) -> None:
        # Given
        promotion_type = "best"
        is_active = True
        product_code = self.product.product_code
        url = "/api/v1/promotion-products/add"

        # When: 프로모션에 등록된 적 없는 제품을 추가할 때
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url=url,
                params={"promotion_type": promotion_type, "product_code": product_code, "is_active": is_active},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then: 새로운 프로모션이 생성되는지 확인
        assert response.status_code == 200
        assert data["product_code"] == product_code
        assert data["product_name"] == self.product.name
        assert data["is_active"] == is_active
        assert data["promotion_type"] == promotion_type

    async def test_delete_nonexistent_promotion_product(self) -> None:
        # Given
        product_code = self.product.product_code
        promotion_type = "best"
        url = "/api/v1/promotion-products/delete"

        # When: 존재하지 않는 프로모션을 삭제하려고 할 때
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                url=url,
                params={"product_code": product_code, "promotion_type": promotion_type},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then: 삭제 요청에 대한 오류 메시지가 반환되는지 확인
        assert response.status_code == 404
        assert (
            data["data"]
            == f"No PromotionProduct found with product_code={product_code}, promotion_type={promotion_type}"
        )

    async def test_update_nonexistent_promotion_product(self) -> None:
        # Given
        product_code = self.product.product_code
        promotion_type = "best"  # 존재하지 않는 프로모션의 타입
        is_active = True
        new_promotion_type = "md_pick"
        new_is_active = True
        url = "/api/v1/promotion-products/update"

        # When: 존재하지 않는 프로모션을 업데이트하려고 할 때
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.patch(
                url=url,
                params={
                    "product_code": product_code,
                    "promotion_type": promotion_type,
                    "is_active": is_active,
                    "new_promotion_type": new_promotion_type,
                    "new_is_active": new_is_active,
                },
                headers={"Accept": "application/json"},
            )
        data = response.json()

        # Then: 업데이트 요청에 대한 오류 메시지가 반환되는지 확인
        assert response.status_code == 404
        assert data["data"] == f"{product_code}의 {promotion_type}은 등록되어 있지 않은 프로모션입니다."
