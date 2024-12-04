from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from tortoise.contrib.test import TestCase

from app.cart.models.cart import Cart
from app.product.models.product import CountProduct, Option, OptionImage, Product
from app.user.models.user import User
from main import app
from tests.utils import generate_mock_jwt


class TestCartRouter(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        # Given: 공통 데이터 생성
        self.user = await User.create(
            name="Test User",
            email="testuser@example.com",
            phone="123-456-7890",
            login_id="testuser",
            user_type="guest",
            password="hashedpassword",
        )
        self.product = await Product.create(
            name="Test Product",
            price=100.00,
            discount=10.00,
            discount_option="percent",
            origin_price=110.00,
            description="Test description",
            detail="Test detail",
            brand="Test Brand",
            status="Y",
            product_code="TEST001",
        )
        self.option = await Option.create(
            size="M",
            color="Red",
            color_code="#FF0000",
            product=self.product,
        )
        self.option_image = await OptionImage.create(
            image_url="http://example.com/image.jpg",
            option=self.option,
        )
        self.count_product = await CountProduct.create(
            product=self.product,
            option=self.option,
            count=50,
        )

    @patch("app.user.services.auth_service.AuthenticateService.get_user_id", new_callable=AsyncMock)
    async def test_get_list(self, mock_get_user_id: AsyncMock) -> None:
        """
        GWT 기반: 장바구니 조회 테스트
        """
        # Given: 장바구니 데이터 생성
        await Cart.create(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=2,
        )
        mock_get_user_id.return_value = self.user.id

        # 테스트용 JWT 생성
        mock_token = generate_mock_jwt({"user_id": self.user.id}, secret_key="your-jwt-secret-key")

        # When: 장바구니 조회 요청
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url="/api/v1/cart/",
                headers={"Accept": "application/json", "Authorization": f"Bearer {mock_token}"},
            )

        # Then: 응답 코드와 데이터 검증
        assert response.status_code == 200
        response_data = response.json()
        assert "items" in response_data
        assert isinstance(response_data["items"], list)
        assert len(response_data["items"]) == 1  # 생성된 장바구니 데이터 개수
        assert response_data["items"][0]["product_name"] == "Test Product"
        assert response_data["items"][0]["product_amount"] == 2

    @patch("app.user.services.auth_service.AuthenticateService.get_user_id", new_callable=AsyncMock)
    async def test_add_to_cart(self, mock_get_user_id: AsyncMock) -> None:
        """
        GWT 기반: 장바구니에 상품 추가 테스트
        """
        # Given
        mock_get_user_id.return_value = self.user.id
        mock_token = generate_mock_jwt({"user_id": self.user.id}, secret_key="your-jwt-secret-key")
        cart_item = {
            "product_id": self.product.id,
            "option_id": self.option.id,
            "product_count": 2,
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/cart/",
                json=cart_item,
                headers={"Accept": "application/json", "Authorization": f"Bearer {mock_token}"},
            )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["product_id"] == self.product.id
        assert response_data["option_id"] == self.option.id
        assert response_data["product_amount"] == 2

    @patch("app.user.services.auth_service.AuthenticateService.get_user_id", new_callable=AsyncMock)
    async def test_update_cart(self, mock_get_user_id: AsyncMock) -> None:
        """
        GWT 기반: 장바구니 상품 수량 수정 테스트
        """
        # Given
        mock_get_user_id.return_value = self.user.id
        cart = await Cart.create(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=1,
        )
        mock_token = generate_mock_jwt({"user_id": self.user.id}, secret_key="your-jwt-secret-key")
        updated_item = {
            "product_id": self.product.id,
            "option_id": self.option.id,
            "product_count": 5,
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.patch(
                url="/api/v1/cart/",
                json=updated_item,
                headers={"Accept": "application/json", "Authorization": f"Bearer {mock_token}"},
            )

        # Then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["product_amount"] == 5

    @patch("app.user.services.auth_service.AuthenticateService.get_user_id", new_callable=AsyncMock)
    async def test_delete_cart(self, mock_get_user_id: AsyncMock) -> None:
        """
        GWT 기반: 장바구니 상품 삭제 테스트
        """
        # Given
        mock_get_user_id.return_value = self.user.id
        cart = await Cart.create(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=1,
        )
        mock_token = generate_mock_jwt({"user_id": self.user.id}, secret_key="your-jwt-secret-key")

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                url=f"/api/v1/cart/?product_id={self.product.id}&option_id={self.option.id}",
                headers={"Accept": "application/json", "Authorization": f"Bearer {mock_token}"},
            )

        # Then
        assert response.status_code == 204
        cart_exists = await Cart.filter(id=cart.id).exists()
        assert not cart_exists
