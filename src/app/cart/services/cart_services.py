from typing import List

from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist, ValidationError

from app.cart.dtos.cart_response import CartItemResponse, CartResponse
from app.cart.models.cart import Cart
from app.product.models.product import CountProduct, Option


class CartService:
    @staticmethod
    async def get_cart(user_id: int) -> CartResponse:
        # 해당 유저의 모든 장바구니 가져오기 (product, option 관계 포함)
        cart = await Cart.filter(user_id=user_id).prefetch_related("product", "option", "option__images").all()

        # 장바구니가 없다면
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart does not exist")

        # 각 장바구니 아이템을 CartItemResponse로 맵핑
        items: List[CartItemResponse] = [
            CartItemResponse(
                user_id=item.user_id,  # type: ignore
                product_id=item.product_id,  # type: ignore
                product_name=item.product.name,
                product_count=item.product_count,
                product_color=item.option.color,
                product_size=item.option.size,
                product_price=float(item.product.price),
                product_image_url=item.option.images[0].image_url if item.option.images else "",
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
    async def add_to_cart(
        user_id: int, product_id: int, color: str, size: str, product_count: int = 1
    ) -> CartItemResponse:
        # 주어진 color와 size로 Option을 조회
        option, stock_count = await Option.get_option_with_stock(product_id, color, size)

        # 재고 초과 확인
        if product_count > stock_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Requested quantity exceeds available stock"
            )

        # 유저 장바구니에서 동일한 상품과 옵션이 있는지 확인
        user_cart = (
            await Cart.filter(user_id=user_id, product_id=product_id, option_id=option.id)
            .prefetch_related("product", "option", "option__images")
            .first()
        )

        # 해당 장바구니에 동일한 상품과 옵션이 있을 때 (수량 업데이트)
        if user_cart:
            if user_cart.product_count + product_count > stock_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Requested quantity exceeds available stock.",
                )

            user_cart.product_count += product_count
            await user_cart.save()

            return CartItemResponse(
                user_id=user_cart.user,
                product_id=user_cart.product,
                product_name=user_cart.product.name,
                product_count=user_cart.product_count,
                product_color=user_cart.option.color,
                product_size=user_cart.option.size,
                product_price=float(user_cart.product.price),
                product_image_url=user_cart.option.images[0].image_url if user_cart.option.images else "",
            )

        # 장바구니에 동일한 상품과 옵션이 없을 때 (새로운 상품 추가)
        new_cart = await Cart.create(
            user_id=user_id, product_id=product_id, option_id=option.id, product_count=product_count
        )
        return CartItemResponse(
            user_id=new_cart.user,
            product_id=new_cart.product,
            product_name=new_cart.product.name,
            product_count=new_cart.product_count,
            product_color=new_cart.option.color,
            product_size=new_cart.option.size,
            product_price=float(new_cart.product.price),
            product_image_url=new_cart.option.images[0].image_url if new_cart.option.images else "",
        )

    @staticmethod
    async def update_cart(user_id: int, product_id: int, color: str, size: str, product_count: int) -> CartItemResponse:
        # Option과 재고를 클래스 메서드를 사용해 가져오기
        option, stock_count = await Option.get_option_with_stock(product_id, color, size)

        # 재고 초과 확인
        if product_count > stock_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock.",
            )

        # 유저의 장바구니에서 해당 상품과 옵션 조회
        try:
            user_cart = await Cart.get(user_id=user_id, product_id=product_id, option_id=option.id).prefetch_related(
                "product", "option", "option__images"
            )
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item does not exist.",
            )

        # 장바구니의 수량 업데이트
        user_cart.product_count = product_count
        await user_cart.save()

        return CartItemResponse(
            user_id=user_cart.user,
            product_id=user_cart.product,
            product_name=user_cart.product.name,
            product_count=user_cart.product_count,
            product_color=user_cart.option.color,
            product_size=user_cart.option.size,
            product_price=float(user_cart.product.price),
            product_image_url=user_cart.option.images[0].image_url if user_cart.option.images else "",
        )

    @staticmethod
    async def delete_cart(user_id: int, product_id: int, color: str, size: str) -> None:
        try:
            # 주어진 product_id, color, size에 해당하는 Option 조회
            option = await Option.get(product_id=product_id, color=color, size=size)
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified option does not exist.",
            )

        try:
            # 유저의 장바구니에서 해당 상품과 옵션 조회
            user_cart = await Cart.get(user_id=user_id, product_id=product_id, option_id=option.id)
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item does not exist.",
            )

        # 장바구니 항목 삭제
        await user_cart.delete()
