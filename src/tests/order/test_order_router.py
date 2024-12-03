# tests/order/test_order_router.py
from decimal import Decimal

from httpx import AsyncClient
from starlette.testclient import TestClient
from tortoise.contrib.test import TestCase

from app.order.dtos.order_request import UpdateShippingRequest
from app.order.models.order import NonUserOrder, NonUserOrderProduct
from app.order.services.order_services import OrderService
from app.product.models.product import CountProduct, Option, Product
from main import app


class TestOrderRouter(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        # 테스트용 상품 생성
        self.test_product = await Product.create(
            name="Test Product", price=Decimal("85000"), origin_price=Decimal("100000"), product_code="TEST001"
        )

        # 테스트용 옵션 생성
        self.test_option = await Option.create(product=self.test_product, size="M", color="Red", color_code="#FF0000")

        self.test_stock = await CountProduct.create(
            product=self.test_product, option=self.test_option, count=10  # 초기 재고 10개
        )

        # 테스트용 주문 생성
        self.test_order = await NonUserOrder.create(
            name="Test User",
            phone="01012345678",
            shipping_address="Test Address",
            detail_address="Detail Address",
            request="Test Request",
        )

        # 테스트용 주문상품 생성
        self.test_order_product = await NonUserOrderProduct.create(
            order=self.test_order,
            product=self.test_product,
            option_id=self.test_option.id,
            quantity=1,
            price=Decimal("85000"),
            current_status="PENDING",
        )

    async def test_verify_order(self) -> None:
        # Given
        order = await NonUserOrder.get(id=self.test_order.pk)
        assert order.phone == "01012345678"

        # When
        verification_data = {"order_number": f"ORD-{self.test_order.pk}", "phone": "01012345678"}
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/order/verify", headers={"Accept": "application/json"}, json=verification_data
            )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "01012345678"

    async def test_create_order(self) -> None:
        # Given
        order_data = {
            "name": "New User",
            "phone": "01087654321",
            "shipping_address": "New Address",
            "detail_address": "Detail Address",
            "request": "Test Request",
            "products": [
                {"product_id": self.test_product.id, "option_id": self.test_option.id, "quantity": 1, "price": "85000"}
            ],
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/order", headers={"Accept": "application/json"}, json=order_data)

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New User"
        assert len(data["products"]) == 1

    async def test_verify_order_with_wrong_phone(self) -> None:
        # Given
        verification_data = {"order_number": f"ORD-{self.test_order.pk}", "phone": "01000000000"}  # 잘못된 전화번호

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/order/verify", headers={"Accept": "application/json"}, json=verification_data
            )

        # Then
        assert response.status_code == 403  # 권한 없음

    async def test_update_shipping_info(self) -> None:
        # Given
        shipping_data = {
            "order_id": self.test_order.pk,
            "courier": "Test Courier",
            "tracking_number": "1234567890",
            "shipping_status": "SHIPPING",
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                "/api/v1/order/shipping", headers={"Accept": "application/json"}, json=shipping_data
            )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["courier"] == "Test Courier"
        assert data["tracking_number"] == "1234567890"

    async def test_batch_update_status(self) -> None:
        # Given
        batch_data = {"order_ids": [self.test_order.pk], "status": "SHIPPING"}

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                "/api/v1/order/batch-status", headers={"Accept": "application/json"}, json=batch_data
            )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 1
        assert data["status"] == "SHIPPING"

    async def test_get_order_statistics(self) -> None:
        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/order/statistics", headers={"Accept": "application/json"})

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "total_orders" in data
        assert "pending_orders" in data

    async def test_search_orders(self) -> None:
        # Given
        # 테스트용 주문 생성
        order = await NonUserOrder.create(
            name="Test User",
            phone="01012345678",
            shipping_address="Test Address",
            detail_address="Detail Address",
            request="Test Request",
        )

        # 주문 상품 생성
        await NonUserOrderProduct.create(
            order=order,
            product=self.test_product,
            option_id=self.test_option.id,
            quantity=1,
            price=Decimal("85000"),
            current_status="PENDING",
        )

        search_params = {"order_status": "PENDING", "page": "1", "limit": "10"}

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/order/search", headers={"Accept": "application/json"}, params=search_params
            )

        # Then
        assert response.status_code == 200
        data = response.json()

        # OrderSearchResponse 구조 검증
        assert "orders" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data

        # 검색 결과 데이터 검증
        orders = data["orders"]
        assert len(orders) > 0
        first_order = orders[0]

        assert "id" in first_order
        assert "name" in first_order
        assert "phone" in first_order
        assert "products" in first_order

        # 주문 상품 검증
        products = first_order["products"]
        assert len(products) > 0
        assert products[0]["product_id"] == self.test_product.id
        assert products[0]["quantity"] == 1
        assert products[0]["price"] == "85000.00"

    async def test_search_orders_with_status_filter(self) -> None:
        # Given
        # PENDING 상태 주문 생성
        pending_order = await NonUserOrder.create(
            name="Pending User",
            phone="01012345678",
            shipping_address="Test Address",
        )
        await NonUserOrderProduct.create(
            order=pending_order,
            product=self.test_product,
            option_id=self.test_option.id,
            quantity=1,
            price=Decimal("85000"),
            current_status="PENDING",
        )

        # SHIPPING 상태 주문 생성
        shipping_order = await NonUserOrder.create(
            name="Shipping User",
            phone="01087654321",
            shipping_address="Test Address 2",
        )
        await NonUserOrderProduct.create(
            order=shipping_order,
            product=self.test_product,
            option_id=self.test_option.id,
            quantity=1,
            price=Decimal("85000"),
            current_status="SHIPPING",
        )

        # When - PENDING 상태만 검색
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/order/search", headers={"Accept": "application/json"}, params={"order_status": "PENDING"}
            )

        # Then
        assert response.status_code == 200
        data = response.json()
        orders = data["orders"]

        # PENDING 상태 주문만 포함되어 있는지 확인
        assert all(order["order_status"] == "PENDING" for order in orders)
        assert any(order["name"] == "Pending User" for order in orders)
        assert not any(order["name"] == "Shipping User" for order in orders)
