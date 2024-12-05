from fastapi import HTTPException
from tortoise.contrib.test import TestCase

from app.cart.models.cart import Cart
from app.cart.services.cart_services import CartService
from app.product.models.product import CountProduct, Option, OptionImage, Product
from app.user.models.user import User


class TestCartService(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        # Given: 공통 테스트 데이터 생성
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

    async def test_get_cart_success(self) -> None:
        # Given
        await Cart.create(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=2,
        )

        # When
        response = await CartService.get_cart(user_id=self.user.id)

        # Then
        assert response.total_count == 2
        assert len(response.items) == 1
        assert response.items[0].product_name == "Test Product"
        assert response.items[0].option_id == self.option.id

    async def test_get_cart_empty(self) -> None:
        # When & Then
        try:
            await CartService.get_cart(user_id=self.user.id)
        except HTTPException as e:
            assert e.status_code == 404
            assert e.detail == "Cart does not exist"

    async def test_add_to_cart_success(self) -> None:
        # When
        response = await CartService.add_to_cart(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=1,
        )

        # Then
        assert response.product_name == "Test Product"
        assert response.product_amount == 1
        assert response.option_id == self.option.id

    async def test_add_to_cart_stock_exceeded(self) -> None:
        # When & Then
        try:
            await CartService.add_to_cart(
                user_id=self.user.id,
                product_id=self.product.id,
                option_id=self.option.id,
                product_count=100,
            )
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "Requested quantity exceeds available stock."

    async def test_add_to_cart_user_cart_already_exists(self) -> None:
        # Given
        cart = await Cart.create(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=2,
        )

        # When
        response = await CartService.add_to_cart(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=1,
        )

        # Then
        updated_cart = await Cart.get(id=cart.id)
        assert updated_cart.product_count == 3
        assert response.product_amount == 3

    async def test_add_to_cart_user_cart_exceed_stock(self) -> None:
        # Given
        await Cart.create(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=48,
        )

        # When & Then
        try:
            await CartService.add_to_cart(
                user_id=self.user.id,
                product_id=self.product.id,
                option_id=self.option.id,
                product_count=5,
            )
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "Requested quantity exceeds available stock."

    async def test_update_cart_success(self) -> None:
        # Given
        await Cart.create(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=1,
        )

        # When
        response = await CartService.update_cart(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=5,
        )

        # Then
        assert response.product_amount == 5
        assert response.option_id == self.option.id

    async def test_update_cart_exceeding_stock(self) -> None:
        # Given
        await Cart.create(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=1,
        )

        # When & Then
        try:
            await CartService.update_cart(
                user_id=self.user.id,
                product_id=self.product.id,
                option_id=self.option.id,
                product_count=100,
            )
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "Requested quantity exceeds available stock."

    async def test_update_cart_cart_not_found(self) -> None:
        # When & Then
        try:
            await CartService.update_cart(
                user_id=self.user.id,
                product_id=self.product.id,
                option_id=self.option.id,
                product_count=2,
            )
        except HTTPException as e:
            assert e.status_code == 404
            assert e.detail == "Cart item does not exist."

    async def test_delete_cart_success(self) -> None:
        # Given
        await Cart.create(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
            product_count=1,
        )

        # When
        await CartService.delete_cart(
            user_id=self.user.id,
            product_id=self.product.id,
            option_id=self.option.id,
        )

        # Then
        cart = await Cart.filter(user_id=self.user.id).first()
        assert cart is None

    async def test_delete_cart_non_existing_cart(self) -> None:
        # When & Then
        try:
            await CartService.delete_cart(
                user_id=self.user.id,
                product_id=self.product.id,
                option_id=self.option.id,
            )
        except HTTPException as e:
            assert e.status_code == 404
            assert e.detail == "Cart item does not exist."
