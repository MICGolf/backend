# tests/order/test_order_services.py
from decimal import Decimal

from tortoise.contrib.test import TestCase

from app.order.dtos.order_request import (
    BatchOrderStatusRequest,
    CreateOrderRequest,
    OrderProductRequest,
    OrderVerificationRequest,
    UpdateShippingRequest,
)
from app.order.models.order import NonUserOrder, NonUserOrderProduct
from app.order.services.order_services import OrderService
from app.product.models.product import CountProduct, Option, Product


class TestOrderServices(TestCase):
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

        # 테스트용 재고 생성
        self.test_stock = await CountProduct.create(
            product=self.test_product,
            option=self.test_option,
            count=10,  # 초기 재고 10개
        )

    async def test_create_order_service(self) -> None:
        # Given
        request = CreateOrderRequest(
            name="Test User",
            phone="01012345678",
            shipping_address="Test Address",
            detail_address="Detail Address",
            request="Test Request",
            products=[
                OrderProductRequest(
                    product_id=self.test_product.id,
                    option_id=self.test_option.id,
                    quantity=1,
                    price=Decimal("85000"),
                )
            ],
        )

        # When
        response = await OrderService.create_order(request)

        # Then
        assert response.name == "Test User"
        assert response.phone == "01012345678"
        assert len(response.products) == 1
        assert response.products[0].quantity == 1

    async def test_get_order_service(self) -> None:
        # Given
        order = await NonUserOrder.create(name="Test User", phone="01012345678", shipping_address="Test Address")
        order_product = await NonUserOrderProduct.create(
            order=order,
            product=self.test_product,
            option_id=self.test_option.id,
            quantity=1,
            price=Decimal("85000"),
            current_status="PENDING",
        )

        # When
        result = await OrderService.get_order(order.pk)

        # Then
        assert result.id == order.pk
        assert result.name == "Test User"
        assert len(result.products) == 1
        assert result.products[0].price == Decimal("85000")

    async def test_update_shipping_info_service(self) -> None:
        # Given
        order = await NonUserOrder.create(name="Test User", phone="01012345678", shipping_address="Test Address")
        order_product = await NonUserOrderProduct.create(
            order=order,
            product=self.test_product,
            option_id=self.test_option.id,
            quantity=1,
            price=Decimal("85000"),
            current_status="PENDING",
        )

        # When
        shipping_request = UpdateShippingRequest(
            order_id=order.pk,
            courier="Test Courier",
            tracking_number="1234567890",
            shipping_status="SHIPPING",
        )
        result = await OrderService.update_shipping_info(shipping_request)

        # Then
        assert result.courier == "Test Courier"
        assert result.tracking_number == "1234567890"
        assert result.status == "SHIPPING"

    async def test_batch_update_status_service(self) -> None:
        # Given
        order1 = await NonUserOrder.create(name="Test User 1", phone="01012345678", shipping_address="Test Address")
        order2 = await NonUserOrder.create(name="Test User 2", phone="01087654321", shipping_address="Test Address 2")

        # When
        request = BatchOrderStatusRequest(order_ids=[order1.pk, order2.pk], status="SHIPPING")
        result = await OrderService.batch_update_status(request)

        # Then
        assert result.updated_count == 2
        assert result.status == "SHIPPING"

    async def test_check_and_update_stock_service(self) -> None:
        # Given
        initial_stock = 10
        requested_quantity = 5

        # When
        result = await OrderService.check_and_update_stock(
            product_id=self.test_product.id,
            option_id=self.test_option.id,
            quantity=requested_quantity,
        )

        # Then
        assert result.has_sufficient_stock == True
        assert result.available_quantity == initial_stock

        # 재고 업데이트 확인
        updated_stock = await CountProduct.get(product=self.test_product, option=self.test_option)
        assert updated_stock.count == initial_stock - requested_quantity

    async def test_get_order_statistics_service(self) -> None:
        # Given
        await NonUserOrderProduct.create(
            order=await NonUserOrder.create(name="Test User", phone="01012345678", shipping_address="Test Address"),
            product=self.test_product,
            option_id=self.test_option.id,
            quantity=1,
            price=Decimal("85000"),
            current_status="PENDING",
        )

        # When
        result = await OrderService.get_order_statistics()

        # Then
        assert result.total_orders >= 1
        assert result.pending_orders >= 1

    async def test_verify_order_owner_service(self) -> None:
        # Given
        order = await NonUserOrder.create(name="Test User", phone="01012345678", shipping_address="Test Address")
        verification = OrderVerificationRequest(order_number=f"ORD-{order.pk}", phone="01012345678")

        # When
        result = await OrderService.verify_order_owner(order.pk, verification)

        # Then
        assert result.is_owner == True

    async def test_verify_order_owner_service_fail(self) -> None:
        # Given
        order = await NonUserOrder.create(name="Test User", phone="01012345678", shipping_address="Test Address")
        verification = OrderVerificationRequest(order_number=f"ORD-{order.pk}", phone="01087654321")  # 잘못된 전화번호

        # When
        result = await OrderService.verify_order_owner(order.pk, verification)

        # Then
        assert result.is_owner == False
