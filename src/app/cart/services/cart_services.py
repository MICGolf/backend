from typing import List

from tortoise.exceptions import DoesNotExist

from app.cart.dtos.cart_response import CartItemResponse, CartResponse
from app.cart.models.cart import Cart


class CartService:
    @staticmethod
    async def get_cart(user_id: int) -> CartResponse | None:
        # 해당 유저의 모든 장바구니 가져오기
        cart = await Cart.filter(user_id=user_id).all()

        # 장바구니가 없다면
        if not cart:
            raise DoesNotExist("Cart does not exist")

        # 각 장바구니 아이템을 CartItemResponse로 맵핑
        items: List[CartItemResponse] = [
            CartItemResponse(
                user_id=item.user,
                product_id=item.product,
                product_count=item.product_count,
            )
            for item in cart
        ]

        # 해당 아이템의 장바구니 내 갯수 계산
        total_count = sum(item.product_count for item in cart)

        # 전체 장바구니 응답 반환
        return CartResponse(
            items=items,
            total_count=total_count,
        )

    @staticmethod
    async def add_to_cart(user_id: int, product_id: int, product_count: int = 1) -> CartItemResponse:
        # 유저 장바구니에 동일한 상품이 있는지 확인
        user_cart = await Cart.filter(user_id=user_id, product_id=product_id).first()

        # 해당 장바구니에 동일한 상품이 있을 때 (수량 업데이트)
        if user_cart:
            user_cart.product_count += product_count
            await user_cart.save()
            return CartItemResponse(
                user_id=user_cart.user,
                product_id=user_cart.product,
                product_count=user_cart.product_count,
            )

        # 장바구니에 동일한 상품이 없을 때 (새로운 상품 추가)
        new_cart = await Cart.create(user_id=user_id, product_id=product_id, product_count=product_count)
        return CartItemResponse(
            user_id=new_cart.user,
            product_id=new_cart.product,
            product_count=new_cart.product_count,
        )

    @staticmethod
    async def update_cart(user_id: int, product_id: int, product_count: int) -> CartItemResponse:
        user_cart = await Cart.get(user_id=user_id, product_id=product_id)
        user_cart.product_count = product_count
        await user_cart.save()
        return CartItemResponse(
            user_id=user_cart.user,
            product_id=user_cart.product,
            product_count=user_cart.product_count,
        )

    @staticmethod
    async def delete_cart(user_id: int, product_id: int) -> None:
        user_cart = await Cart.get(user_id=user_id, product_id=product_id)
        await user_cart.delete()
        return None
