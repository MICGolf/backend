from fastapi import APIRouter, Body, Depends, status

from app.cart.dtos.cart_request import CartItemRequest
from app.cart.dtos.cart_response import CartItemResponse, CartResponse
from app.cart.services.cart_services import CartService
from app.user.services.auth_service import AuthenticateService

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartResponse, summary="장바구니 조회")
async def get_cart(
    user_id: int = Depends(AuthenticateService().get_user_id),
) -> CartResponse:
    """
    유저의 장바구니를 조회합니다.
    """
    return await CartService.get_cart(user_id)


@router.post("/", response_model=CartItemResponse, summary="장바구니에 상품 추가")
async def add_to_cart(
    cart_item: CartItemRequest,
    user_id: int = Depends(AuthenticateService().get_user_id),
) -> CartItemResponse:
    """
    장바구니에 상품을 추가합니다. 이미 상품이 있으면 수량을 업데이트합니다.
    """
    return await CartService.add_to_cart(
        user_id=user_id,
        product_id=cart_item.product_id,
        option_id=cart_item.option_id,
        product_count=cart_item.product_count,
    )


@router.patch("/", response_model=CartItemResponse, summary="장바구니 상품 수량 수정")
async def update_cart(
    cart_item: CartItemRequest,
    user_id: int = Depends(AuthenticateService().get_user_id),
) -> CartItemResponse:
    """
    장바구니에서 특정 상품의 수량을 수정합니다.
    """
    return await CartService.update_cart(
        user_id=user_id,
        product_id=cart_item.product_id,
        option_id=cart_item.option_id,
        product_count=cart_item.product_count,
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="장바구니 상품 삭제")
async def delete_cart(
    product_id: int,
    option_id: int,
    user_id: int = Depends(AuthenticateService().get_user_id),
) -> None:
    """
    장바구니에서 특정 상품을 삭제합니다.
    """
    await CartService.delete_cart(
        user_id=user_id,
        product_id=product_id,
        option_id=option_id,
    )
