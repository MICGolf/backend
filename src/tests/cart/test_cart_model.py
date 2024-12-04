from httpx import AsyncClient
from tortoise.contrib.test import TestCase

from app.cart.models.cart import Cart
from app.product.models.product import CountProduct, Option, Product
from app.user.models.user import User
from main import app


class TestCartModel(TestCase):
    async def test_cart_model(self) -> None:
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            # Given: 사용자, 제품, 옵션, 재고 생성
            user = await User.create(
                name="TestName",
                email="test@test.com",
                phone="01012345678",
                login_id="Test123",
                password="Password123!",
                user_type="guest",
            )
            product = await Product.create(
                name="TestProduct",
                price=20.00,
                origin_price=25.00,
                discount=5.00,
                discount_option="percent",
                product_code="TESTCODE",
            )
            option = await Option.create(size="L", color="Red", color_code="#FF0000", product=product)
            await CountProduct.create(product=product, option=option, count=50)  # 재고 50개

            # When: 장바구니에 동일한 사용자, 제품, 옵션으로 아이템 추가
            cart_item_1 = await Cart.create(user=user, product=product, option=option, product_count=2)
            cart_item_2 = None
            duplicate_error = None
            try:
                cart_item_2 = await Cart.create(user=user, product=product, option=option, product_count=3)
            except Exception as e:
                duplicate_error = str(e)

            assert cart_item_1 is not None
            assert cart_item_2 is None
            assert duplicate_error is not None, "Duplicate error message is None"
            assert "(1062" in duplicate_error.lower()
            assert "duplicate entry" in duplicate_error.lower()

            # Then: 저장된 데이터 확인
            cart_items = await Cart.filter(user=user, product=product, option=option)
            assert len(cart_items) == 1
            assert cart_items[0].product_count == 2

            stock = await CountProduct.filter(product=product, option=option).first()
            assert stock is not None, "Stock is None"
            assert stock.count == 50
