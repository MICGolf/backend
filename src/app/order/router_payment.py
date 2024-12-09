from typing import Any

from fastapi import APIRouter, Depends

from app.order.dtos.payment_request import PaymentApproveRequestDTO, PaymentReserveRequestDTO
from app.order.dtos.payment_response import PaymentReserveResponseDTO
from app.order.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["비회원/회원_결제"])


@router.post(
    "/reserve",
    response_model=PaymentReserveResponseDTO,
)
async def reserve_payment(
    request: PaymentReserveRequestDTO,
    payment_service: PaymentService = Depends(),
) -> PaymentReserveResponseDTO:
    """Step 1: 결제 예약"""
    return await payment_service.reserve_payment(payment_data=request)


@router.post("/approve")
async def approve_payment(
    request: PaymentApproveRequestDTO,
    payment_service: PaymentService = Depends(),
) -> None:
    """Step 3: 결제 승인"""
    await payment_service.approve_payment(payment_data=request)
