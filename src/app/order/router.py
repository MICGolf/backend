from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query

from app.order.dtos.order_request import (
    BatchOrderStatusRequest,
    CreateOrderRequest,
    OrderClaimRequest,
    OrderSearchRequest,
    OrderVerificationRequest,
    PurchaseOrderRequest,
    UpdateOrderStatusRequest,
    UpdatePurchaseStatusRequest,
    UpdateShippingRequest,
)
from app.order.dtos.order_response import (
    BatchUpdateStatusResponse,
    OrderResponse,
    OrderSearchResponse,
    OrderStatisticsResponse,
    PurchaseOrderResponse,
    ShippingStatusResponse,
    StockCheckResponse,
    UpdateOrderStatusResponse,
)
from app.order.services.order_services import OrderService


class OrderStatus(Enum):
    PENDING = "PENDING"  # 주문 완료, 결제 대기
    PAID = "PAID"  # 결제 완료
    PREPARING = "PREPARING"  # 상품 준비중
    SHIPPING = "SHIPPING"  # 배송중
    DELIVERED = "DELIVERED"  # 배송 완료
    CANCELLED = "CANCELLED"  # 주문 취소
    REFUNDED = "REFUNDED"  # 환불 완료


router = APIRouter(prefix="/order", tags=["비회원 주문"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=201,
    summary="비회원 주문 생성",
    description="""
        비회원 주문을 생성합니다.
        - 주문자 정보와 배송지 정보 필요
        - 하나 이상의 상품 필수
        - 각 상품에 대한 옵션 지정 필수
        - 재고 확인 후 생성 (재고 부족 시 400 에러)
        - 주문 생성 시 PENDING 상태로 시작
        """,
)
async def create_order(request: CreateOrderRequest) -> OrderResponse:
    return await OrderService.create_order(request)


@router.post(
    "/verify",
    response_model=OrderResponse,
    summary="비회원 주문 조회",
    description="주문번호와 주문자 정보로 비회원 주문을 조회합니다.",
)
async def get_order_by_verification(
    verification: OrderVerificationRequest = Body(..., description="주문자 확인 정보")
) -> OrderResponse:
    # ORD-14에서 14 추출
    try:
        order_id = int(verification.order_number.replace("ORD-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order number format")

        # 기존 get_order 로직 재사용
    if not await OrderService.verify_order_owner(order_id, verification):
        raise HTTPException(status_code=403, detail="Invalid verification info")

    return await OrderService.get_order(order_id)


# 회원일 경우 해당기능 사용예정
# @router.get(
#     "/{order_id}",
#     response_model=OrderResponse,
#     summary="주문 상세 조회",
#     description="""
#    주문 번호로 주문 상세 정보를 조회합니다.
#    - 주문 기본 정보
#    - 주문 상품 목록
#    - 배송 정보
#    - 결제 상태
#    """,
# )
# async def get_order(
#     order_id: int = Path(..., description="주문 ID"),
#     verification: OrderVerificationRequest = Body(..., description="주문자 확인 정보(전화번호 등)"),
# ) -> OrderResponse:
#     # 주문자 본인 확인
#     if not await OrderService.verify_order_owner(order_id, verification):
#         raise HTTPException(status_code=403, detail="Invalid verification info")
#     return await OrderService.get_order(order_id)


@router.put(
    "/{order_id}/status",
    status_code=200,
    summary="주문 상태 업데이트",
    description="주문의 상태를 업데이트합니다. (관리자 전용)",
    response_model=UpdateOrderStatusRequest,
)
async def update_order_status(request: UpdateOrderStatusRequest = Body(...)) -> UpdateOrderStatusResponse:
    return await OrderService.update_order_status(request.order_id, request.status)

    # @router.get(
    #     "/tracking/{order_id}",
    #     summary="배송 추적",
    #     description="주문의 배송 상태를 조회합니다.",
    #     response_model=ShippingStatusResponse,  # response_model 추가
    # )
    # async def track_shipping(
    #     order_id: int = Path(..., description="주문 ID"),
    #     verification: OrderVerificationRequest = Query(..., description="주문자 확인 정보"),
    # ) -> ShippingStatusResponse:  # 리턴 타입을 dict -> ShippingStatusResponse로 변경
    #     if not await OrderService.verify_order_owner(order_id, verification):
    #         raise HTTPException(status_code=403, detail="Invalid verification info")
    #     return await OrderService.get_shipping_status(order_id)


@router.put("/shipping", response_model=ShippingStatusResponse, summary="배송 정보 업데이트")
async def update_shipping_info(request: UpdateShippingRequest = Body(...)) -> ShippingStatusResponse:
    return await OrderService.update_shipping_info(request)


@router.get("/search", response_model=OrderSearchResponse, summary="주문 상세 검색")
async def search_orders(
    params: OrderSearchRequest = Depends(),  # 여기서 OrderSearchRequest를 의존성으로 사용
) -> list[OrderResponse]:
    return await OrderService.advanced_search(params)


@router.put("/batch-status", response_model=BatchUpdateStatusResponse, summary="주문 상태 일괄 변경")
async def batch_update_status(request: BatchOrderStatusRequest) -> BatchUpdateStatusResponse:
    return await OrderService.batch_update_status(request)


@router.post(
    "/purchase",
    response_model=PurchaseOrderResponse,
    summary="발주 확인",
    description="""
    주문에 대한 발주를 확인하고 재고를 확인/차감합니다.
    - 재고가 충분한 경우: 재고 차감 후 발주 상태를 CONFIRMED로 설정
    - 재고가 부족한 경우: 발주 상태를 PENDING으로 설정
    반환값에는 주문 정보와 재고 확인 결과가 모두 포함됩니다.
    """,
)
async def update_purchase_order(
    request: PurchaseOrderRequest = Body(..., description="발주 확인 요청")
) -> PurchaseOrderResponse:
    order_response, stock_check = await OrderService.update_purchase_order(request)
    return PurchaseOrderResponse(order=order_response, stock_check=stock_check)


@router.get("/statistics", response_model=OrderStatisticsResponse, summary="주문 통계")
async def get_order_statistics() -> OrderStatisticsResponse:
    return await OrderService.get_order_statistics()


# router.py
@router.post("/claim", response_model=OrderResponse, summary="주문 클레임 처리")
async def handle_order_claim(request: OrderClaimRequest = Body(...)) -> OrderResponse:
    return await OrderService.handle_order_claim(request)


@router.put("/purchase-status", response_model=OrderResponse, summary="발주 상태 업데이트")
async def update_purchase_status(request: UpdatePurchaseStatusRequest = Body(...)) -> OrderResponse:
    return await OrderService.update_purchase_status(request)


@router.get(
    "/stock-check/{product_id}",
    response_model=StockCheckResponse,
    summary="상품 재고 확인",
    description="상품의 재고를 확인하고 필요한 경우 재고를 차감합니다.",
)
async def check_stock(
    product_id: int = Path(..., description="상품 ID"),
    option_id: int = Query(..., description="옵션 ID"),
    quantity: int = Query(..., gt=0, description="확인할 수량"),
) -> StockCheckResponse:
    return await OrderService.check_and_update_stock(product_id, option_id, quantity)
