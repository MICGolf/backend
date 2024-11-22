from tortoise.contrib.test import TestCase

from app.product.models.product import DiscountOption, Product
from app.promotion_product.dtos.promotion_response import PromotionProductListResponse, PromotionProductResponse
from app.promotion_product.models.promotion_product import PromotionProduct, PromotionType
from app.promotion_product.services.promotion_services import PromotionProductService


class TestPromotionProductService(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        # 샘플 데이터 생성
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

    async def test_get_promotion_products(self) -> None:
        # Given
        promotion_type = "md_pick"
        page = 1
        size = 10

        # When
        response: PromotionProductListResponse = await PromotionProductService.get_promotion_products(
            promotion_type=promotion_type, page=page, size=size
        )

        # Then
        assert isinstance(response.items, list)
        for item in response.items:
            assert isinstance(item, PromotionProductResponse)
        assert response.page == page
        assert response.size == size
