from typing import List

from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist

from app.cart.dtos.cart_response import CartItemResponse, CartResponse
from app.cart.models.cart import Cart
from app.product.models.product import CountProduct, Option


class CartService:
    @staticmethod
    async def get_cart(user_id: int) -> CartResponse:
        # 해당 유저의 모든 장바구니 가져오기 (product, option 관계 포함)
        cart = await Cart.filter(user_id=user_id).prefetch_related("product", "option", "option__images").all()

        # option_id와 product_id 추출
        option_ids = [item.option_id for item in cart]  # type: ignore
        product_ids = [item.product_id for item in cart]  # type: ignore

        # count_product 가져오기
        stock = await CountProduct.filter(option_id__in=option_ids, product_id__in=product_ids).all()

        count_product_map = {(cp.product_id, cp.option_id): cp.count for cp in stock}  # type: ignore

        # 장바구니가 없다면
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart does not exist")

        # 각 장바구니 아이템을 CartItemResponse로 맵핑
        items: List[CartItemResponse] = [
            CartItemResponse(
                cart_id=item.id,
                user_id=item.user_id,  # type: ignore
                product_id=item.product_id,  # type: ignore
                option_id=item.option_id,  # type: ignore
                product_code=item.product.product_code,
                product_name=item.product.name,
                product_image_url=(item.option.images[0].image_url if item.option.images else ""),
                product_color=item.option.color,
                product_size=item.option.size,
                product_amount=item.product_count,
                product_stock=count_product_map.get((item.product_id, item.option_id), 0),  # type: ignore
                origin_price=item.product.origin_price,
                price=float(item.product.price),
                discount=item.product.discount,
                discount_option=item.product.discount_option,
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
        # 주어진 color와 size로 option을 조회
        option, stock_count = await Option.get_option_with_stock(product_id, color, size)

        # 재고 초과 확인
        if product_count > stock_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Requested quantity exceeds available stock."
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
                cart_id=user_cart.id,
                user_id=user_cart.user_id,  # type: ignore
                product_id=user_cart.product_id,  # type: ignore
                option_id=user_cart.option_id,  # type: ignore
                product_code=user_cart.product.product_code,
                product_name=user_cart.product.name,
                product_image_url=(user_cart.option.images[0].image_url if user_cart.option.images else ""),
                product_color=user_cart.option.color,
                product_size=user_cart.option.size,
                product_amount=user_cart.product_count,
                product_stock=stock_count,
                origin_price=user_cart.product.origin_price,
                price=float(user_cart.product.price),
                discount=user_cart.product.discount,
                discount_option=user_cart.product.discount_option,
            )

        # 장바구니에 동일한 상품과 옵션이 없을 때 (새로운 상품 추가)
        new_cart = await Cart.create(
            user_id=user_id,
            product_id=product_id,
            option_id=option.id,
            product_count=product_count,
        )
        new_cart = await Cart.get(id=new_cart.id).prefetch_related("product", "option", "option__images")
        return CartItemResponse(
            cart_id=new_cart.id,
            user_id=new_cart.user_id,  # type: ignore
            product_id=new_cart.product_id,  # type: ignore
            option_id=new_cart.option_id,  # type: ignore
            product_code=new_cart.product.product_code,
            product_name=new_cart.product.name,
            product_image_url=(new_cart.option.images[0].image_url if new_cart.option.images else ""),
            product_color=new_cart.option.color,
            product_size=new_cart.option.size,
            product_amount=new_cart.product_count,
            product_stock=stock_count,
            origin_price=new_cart.product.origin_price,
            price=float(new_cart.product.price),
            discount=new_cart.product.discount,
            discount_option=new_cart.product.discount_option,
        )

    @staticmethod
    async def update_cart(user_id: int, product_id: int, option_id: int, product_count: int) -> CartItemResponse:
        # Option과 재고를 조회
        stock = await CountProduct.filter(option_id=option_id, product_id=product_id).first()
        if not stock or product_count > stock.count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock.",
            )

        # 유저의 장바구니에서 해당 상품과 옵션 조회
        try:
            user_cart = await Cart.get(user_id=user_id, product_id=product_id, option_id=option_id).prefetch_related(
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
            cart_id=user_cart.id,
            user_id=user_cart.user_id,  # type: ignore
            product_id=user_cart.product_id,  # type: ignore
            option_id=user_cart.option_id,  # type: ignore
            product_code=user_cart.product.product_code,
            product_name=user_cart.product.name,
            product_image_url=(user_cart.option.images[0].image_url if user_cart.option.images else ""),
            product_color=user_cart.option.color,
            product_size=user_cart.option.size,
            product_amount=user_cart.product_count,
            product_stock=stock.count,
            origin_price=user_cart.product.origin_price,
            price=float(user_cart.product.price),
            discount=user_cart.product.discount,
            discount_option=user_cart.product.discount_option,
        )

    @staticmethod
    async def delete_cart(user_id: int, product_id: int, option_id: int) -> None:
        try:
            # 유저의 장바구니에서 해당 상품과 옵션 조회
            user_cart = await Cart.get(user_id=user_id, product_id=product_id, option_id=option_id)
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item does not exist.",
            )

        # 장바구니 항목 삭제
        await user_cart.delete()
