# tests/order/test_order_models.py
from decimal import Decimal

from tortoise.contrib.test import TestCase

from app.order.models.order import NonUserOrder, NonUserOrderProduct
from app.product.models.product import Option, Product


class TestOrderModels(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        # 테스트용 상품 생성
        self.test_product = await Product.create(
            name="Test Product",
            price=Decimal("85000"),
            origin_price=Decimal("100000"),
            product_code="TEST001",
        )

        # 테스트용 옵션 생성
        self.test_option = await Option.create(product=self.test_product, size="M", color="Red", color_code="#FF0000")

    async def test_create_non_user_order(self) -> None:
        # Given & When
        order = await NonUserOrder.create(
            name="Test User",
            phone="01012345678",
            shipping_address="Test Address",
            detail_address="Detail Address",
            request="Test Request",
        )

        # Then
        assert order.name == "Test User"
        assert order.phone == "01012345678"
        assert order.shipping_address == "Test Address"
        assert order.detail_address == "Detail Address"

    async def test_create_non_user_order_product(self) -> None:
        # Given
        order = await NonUserOrder.create(name="Test User", phone="01012345678", shipping_address="Test Address")

        # When
        order_product = await NonUserOrderProduct.create(
            order=order,
            product=self.test_product,
            option_id=self.test_option.id,
            quantity=2,
            price=Decimal("85000"),
            current_status="PENDING",
        )

        # Then
        assert order_product.quantity == 2
        assert order_product.price == Decimal("85000")
        assert order_product.current_status == "PENDING"
