from fastapi import HTTPException
from tortoise.contrib.test import TestCase
from tortoise.exceptions import DoesNotExist

from app.product.models.product import DiscountOption, Option, OptionImage, Product
from app.promotion_product.dtos.promotion_request import (
    AddPromotionRequest,
    DeletePromotionRequest,
    UpdatePromotionRequest,
)
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
        request = AddPromotionRequest(
            promotion_type="md_pick",
            is_active=True,
            product_code=self.product.product_code,
        )

        # When
        response = await PromotionProductService.add_promotion_products(request)

        # Then
        assert response.product_name == self.product.name
        assert response.is_active == request.is_active
        assert response.promotion_type == request.promotion_type

    async def test_add_promotion_not_already_exist(self) -> None:
        # Given
        request = AddPromotionRequest(
            promotion_type="best",
            is_active=True,
            product_code=self.product.product_code,
        )

        # When
        response = await PromotionProductService.add_promotion_products(request)

        # Then
        assert isinstance(response, PromotionProductResponse)
        assert response.product_code == request.product_code
        assert response.product_name == self.product.name
        assert response.is_active == request.is_active
        assert response.promotion_type == request.promotion_type
        assert response.image_url == (response.image_url if response.image_url else "")

    async def test_add_promotion_products_error(self) -> None:
        # Given
        request = AddPromotionRequest(
            promotion_type="md_pick",
            is_active=True,
            product_code="randomstring",
        )

        # When
        with self.assertRaises(HTTPException) as context:
            await PromotionProductService.add_promotion_products(request)

        # Then
        exception = context.exception
        assert exception.status_code == 404
        assert exception.detail == f"Product with code '{request.product_code}' does not exist."

    async def test_update_promotion_products(self) -> None:
        # Given
        request = UpdatePromotionRequest(
            product_code=self.product.product_code,
            promotion_type=self.promotion.promotion_type,
            is_active=self.promotion.is_active,
            new_promotion_type=PromotionType.BEST,
            new_is_active=False,
        )

        # When
        response = await PromotionProductService.update_promotion_products(request)

        # Then
        assert response.promotion_type == request.new_promotion_type
        assert response.is_active == request.new_is_active

    async def test_update_promotion_product_does_not_exist(self) -> None:
        # Given
        request = UpdatePromotionRequest(
            product_code="Randomstring",
            promotion_type="best",
            is_active=True,
            new_promotion_type=PromotionType.BEST,
            new_is_active=False,
        )

        # When
        with self.assertRaises(HTTPException) as context:
            await PromotionProductService.update_promotion_products(request)

        # Then
        exception = context.exception
        assert exception.status_code == 404
        assert exception.detail == f"{request.product_code}는 존재하지 않는 상품코드 입니다."

    async def test_update_promotion_promotion_does_not_exist(self) -> None:
        # Given
        request = UpdatePromotionRequest(
            product_code=self.product.product_code,
            promotion_type=PromotionType.BEST,
            is_active=True,
            new_promotion_type=PromotionType.BEST,
            new_is_active=False,
        )

        # When
        with self.assertRaises(HTTPException) as context:
            await PromotionProductService.update_promotion_products(request)

        # Then
        exception = context.exception
        assert exception.status_code == 404
        assert (
            exception.detail
            == f"{request.product_code}의 {request.promotion_type}은 등록되어 있지 않은 프로모션입니다."
        )

    async def test_delete_promotion_products(self) -> None:
        # Given
        request = DeletePromotionRequest(
            product_code=self.product.product_code,
            promotion_type=self.promotion.promotion_type,
        )

        # When
        await PromotionProductService.delete_promotion_products(request)

        # Then
        # 삭제된 프로모션이 더 이상 존재하지 않는지 확인
        with self.assertRaises(DoesNotExist):
            await PromotionProduct.get(product_id=self.product.id, promotion_type=request.promotion_type)

    async def test_delete_product_not_found(self) -> None:
        # Given: 존재하지 않는 product_code
        request = DeletePromotionRequest(
            product_code="nonexistent_code",  # 존재하지 않는 product_code
            promotion_type=self.promotion.promotion_type,
        )

        # When & Then
        with self.assertRaises(HTTPException) as context:
            await PromotionProductService.delete_promotion_products(request)

        # HTTPException 발생 확인
        exception = context.exception
        assert exception.status_code == 404
        assert exception.detail == f"Product with code '{request.product_code}' does not exist."
