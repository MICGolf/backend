import uuid

from tortoise.contrib.test import TestCase
from tortoise.exceptions import DoesNotExist

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

    async def test_add_promotion_products(self) -> None:
        # Given
        promotion_type = "md_pick"
        is_active = True
        product_name = self.product.name

        # When
        response = await PromotionProductService.add_promotion_products(
            promotion_type=promotion_type, product_name=product_name, is_active=is_active
        )

        # Then
        assert response.product_name == product_name
        assert response.is_active == is_active
        assert response.promotion_type == promotion_type

    async def test_update_promotion_products(self) -> None:
        # Given
        product_id = self.product.id
        promotion_type = self.promotion.promotion_type
        is_active = self.promotion.is_active

        # When
        new_promotion_type = PromotionType.BEST
        new_is_active = False
        response = await PromotionProductService.update_promotion_products(
            product_id=product_id,
            promotion_type=promotion_type,
            is_active=is_active,
            new_promotion_type=new_promotion_type,
            new_is_active=new_is_active,
        )

        # Then
        assert response.promotion_type == new_promotion_type
        assert response.is_active == new_is_active

    async def test_update_promotion_product_does_not_exist(self) -> None:
        # Given
        invalid_product_id = int(uuid.uuid4())
        promotion_type = "best"
        is_active = True

        # When
        try:
            await PromotionProductService.update_promotion_products(
                product_id=invalid_product_id,
                promotion_type=promotion_type,
                is_active=is_active,
                new_promotion_type=PromotionType.BEST,
                new_is_active=False,
            )
        except DoesNotExist as e:
            assert (
                str(e)
                == f"No PromotionProduct found with product_id={invalid_product_id}, promotion_type={promotion_type}"
            )

    async def test_delete_promotion_products(self) -> None:
        # Given
        product_id = self.product.id
        promotion_type = self.promotion.promotion_type

        # When
        await PromotionProductService.delete_promotion_products(
            product_id=product_id,
            promotion_type=promotion_type,
        )

        # Then
        # 해당 프로모션 제품이 삭제되었는지 확인
        with self.assertRaises(DoesNotExist):
            await PromotionProduct.get(product_id=product_id, promotion_type=promotion_type)
