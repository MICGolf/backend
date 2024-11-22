import uuid

from tortoise.contrib.test import TestCase

from app.product.models.product import DiscountOption, Product
from app.promotion_product.models.promotion_product import PromotionProduct, PromotionType


class TestPromotionProductModel(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        # Given: product 생성
        product_code = uuid.uuid4().hex[:8]
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
            product_code=product_code,
        )

        # When : promotion 생성
        promotion = await PromotionProduct.create(
            product=self.product, promotion_type=PromotionType.BEST, is_active=True
        )

        # Then
        assert promotion.id is not None
        assert promotion.product.id == self.product.id
        assert promotion.promotion_type == PromotionType.BEST
        assert promotion.is_active is True

    async def test_read_promotion_product(self):
        """Promotion_product 조회"""
        # Given
        product = await Product.create(
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
        promotion = await PromotionProduct.create(product=product, promotion_type=PromotionType.MD_PICK, is_active=True)

        # When
        fetched_promotion = await PromotionProduct.get(id=promotion.id).prefetch_related("product")

        # Then: The promotion product is retrieved with correct data
        assert fetched_promotion.id == promotion.id
        assert fetched_promotion.product.id == product.id
        assert fetched_promotion.promotion_type == PromotionType.MD_PICK
        assert fetched_promotion.is_active is True

    async def test_update_promotion_product(self):
        """Promotion_product 업데이트"""
        # Given
        product = await Product.create(
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
        promotion = await PromotionProduct.create(product=product, promotion_type=PromotionType.MD_PICK, is_active=True)

        # When
        promotion.is_active = False
        promotion.promotion_type = PromotionType.BEST
        await promotion.save()

        # Then
        updated_promotion = await PromotionProduct.get(id=promotion.id).prefetch_related("product")

        assert updated_promotion.is_active is False
        assert updated_promotion.promotion_type == PromotionType.BEST

    async def test_delete_promotion_product(self):
        """Promotion_product 삭제"""
        # Given
        product = await Product.create(
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
        promotion = await PromotionProduct.create(product=product, promotion_type=PromotionType.MD_PICK, is_active=True)

        # When
        await promotion.delete()

        # Then
        deleted_promotion = await PromotionProduct.filter(id=promotion.id).first()
        assert deleted_promotion is None
