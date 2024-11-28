from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from fastapi import APIRouter, Body, HTTPException, Path, Query

from app.order.dtos.order_request import (
    CreateOrderRequest,
    OrderVerificationRequest,
    PaymentRequest,
    RefundRequest,
    UpdateShippingRequest,
)
from app.order.dtos.order_response import OrderResponse, PaymentResponse, ShippingStatusResponse
from app.order.models.order import NonUserPayment
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
   - 주문 생성 시 PENDING 상태로 시작
   """,
)
async def create_order(request: CreateOrderRequest) -> OrderResponse:
    return await OrderService.create_order(request)


@router.get(
    "/verify",
    response_model=OrderResponse,
    summary="비회원 주문 조회",
    description="주문번호와 주문자 정보로 비회원 주문을 조회합니다.",
)
async def get_order_by_verification(
    order_number: str = Query(..., description="주문번호 (예: ORD-123)"),
    phone: str = Query(..., description="주문자 전화번호"),
) -> OrderResponse:
    # ORD-14에서 14 추출
    try:
        order_id = int(order_number.replace("ORD-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order number format")

    # 검증용 request 객체 생성
    verification = OrderVerificationRequest(order_number=order_number, phone=phone)

    # 기존 get_order 로직 재사용
    if not await OrderService.verify_order_owner(order_id, verification):
        raise HTTPException(status_code=403, detail="Invalid verification info")
    return await OrderService.get_order(order_id)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="주문 상세 조회",
    description="""
   주문 번호로 주문 상세 정보를 조회합니다.
   - 주문 기본 정보
   - 주문 상품 목록
   - 배송 정보
   - 결제 상태
   """,
)
async def get_order(
    order_id: int = Path(..., description="주문 ID"),
    verification: OrderVerificationRequest = Query(..., description="주문자 확인 정보(전화번호 등)"),
) -> OrderResponse:
    # 주문자 본인 확인
    if not await OrderService.verify_order_owner(order_id, verification):
        raise HTTPException(status_code=403, detail="Invalid verification info")
    return await OrderService.get_order(order_id)


# @router.post("/payment",
#              response_model=PaymentResponse,
#              status_code=201,
#              summary="주문 결제",
#              description="""
#    주문에 대한 결제를 진행합니다.
#    - 포트원 결제 연동
#    - 결제 금액 검증
#    - 결제 상태 업데이트
#    """
#              )
# async def create_payment(
#         request: PaymentRequest
# ) -> PaymentResponse:
#     return await OrderService.create_payment(request)
#
#
# @router.post("/payment/verify",
#              status_code=200,
#              summary="결제 검증",
#              description="포트원 결제 완료 후 검증을 진행합니다."
#              )
# async def verify_payment(
#         imp_uid: str = Query(..., description="포트원 결제 UID"),
#         merchant_uid: str = Query(..., description="주문 번호")
# ) -> dict:
#     return await OrderService.verify_payment(imp_uid, merchant_uid)
#
#
# @router.post("/payment/cancel",
#              status_code=200,
#              summary="결제 취소",
#              description="결제 취소 및 환불을 진행합니다."
#              )
# async def cancel_payment(
#         request: RefundRequest
# ) -> None:
#     await OrderService.process_refund(request)
#
#
# @router.get("/{order_id}/payment",
#             response_model=PaymentResponse,
#             summary="주문 결제 정보 조회",
#             description="주문의 결제 정보와 상태를 조회합니다."
#             )
# async def get_payment_info(
#         order_id: int = Path(..., description="주문 ID"),
#         verification: OrderVerificationRequest = Query(..., description="주문자 확인 정보")
# ) -> PaymentResponse:
#     if not await OrderService.verify_order_owner(order_id, verification):
#         raise HTTPException(status_code=403, detail="Invalid verification info")
#
#     payment = await OrderService.get_payment_info(order_id)
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")
#     return payment
#


@router.put(
    "/{order_id}/status",
    status_code=200,
    summary="주문 상태 업데이트",
    description="주문의 상태를 업데이트합니다. (관리자 전용)",
    response_model=dict,
)
async def update_order_status(
    order_id: int = Path(..., description="주문 ID"),
    status: str = Query(..., description="변경할 상태"),
    # admin_key: str = Query(..., description="관리자 인증키")
) -> dict[str, Union[int, str]]:
    # if not await OrderService.verify_admin(admin_key):
    #     raise HTTPException(status_code=403, detail="Admin authentication failed")
    return await OrderService.update_order_status(order_id, status)


# router.py
@router.get(
    "/tracking/{order_id}",
    summary="배송 추적",
    description="주문의 배송 상태를 조회합니다.",
    response_model=ShippingStatusResponse,  # response_model 추가
)
async def track_shipping(
    order_id: int = Path(..., description="주문 ID"),
    verification: OrderVerificationRequest = Query(..., description="주문자 확인 정보"),
) -> ShippingStatusResponse:  # 리턴 타입을 dict -> ShippingStatusResponse로 변경
    if not await OrderService.verify_order_owner(order_id, verification):
        raise HTTPException(status_code=403, detail="Invalid verification info")
    return await OrderService.get_shipping_status(order_id)


@router.put("/shipping/{order_id}", response_model=ShippingStatusResponse, summary="배송 정보 업데이트")
async def update_shipping_info(
    order_id: int = Path(..., description="주문 ID"), shipping_info: UpdateShippingRequest = Body(...)
) -> ShippingStatusResponse:
    return await OrderService.update_shipping_info(order_id, shipping_info)
