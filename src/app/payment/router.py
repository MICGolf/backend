from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.payment.dtos.payment_request import (
    PaymentApproveRequestDTO,
    PaymentCheckoutRequestDTO,
    PaymentReserveRequestDTO,
)
from app.payment.dtos.payment_response import (
    PaymentApproveResponseDTO,
    PaymentCheckoutResponseDTO,
    PaymentReserveResponseDTO,
)
from app.payment.services.payment_service import PaymentService
from common.exceptions.payment_exception import PaymentValidationError

router = APIRouter(prefix="/payments", tags=["비회원/회원_결제"])


class PaymentController:
    def __init__(self) -> None:
        self.payment_service: PaymentService = PaymentService()

    @router.post("/reserve", response_model=PaymentReserveResponseDTO)
    async def reserve_payment(self, request: PaymentReserveRequestDTO) -> Dict[str, Any]:
        """Step 1: 결제 예약"""
        try:
            payment_data = {
                "amount": request.amount,
                "name": request.name,
                "payment_method": request.payment_method,
                "payment_type": request.payment_type,
                "buyer_name": request.buyer_name,
                "buyer_email": request.buyer_email,
                "buyer_tel": request.buyer_tel,
            }
            result = await self.payment_service.reserve_payment(
                payment_data=payment_data,
                is_user=bool(request.user_id),
            )
            return dict(result)
        except PaymentValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/checkout", response_model=PaymentCheckoutResponseDTO)
    async def checkout_payment(self, request: PaymentCheckoutRequestDTO) -> Dict[str, Any]:
        """Step 2: 결제 요청"""
        try:
            payment_data = {
                "merchant_uid": request.merchant_uid,
                "card_number": request.card_number,
                "expiry": request.expiry,
                "birth": request.birth,
                "pwd_2digit": request.pwd_2digit,
            }
            result = await self.payment_service.checkout_payment(payment_data)
            return dict(result)
        except PaymentValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/approve", response_model=PaymentApproveResponseDTO)
    async def approve_payment(self, request: PaymentApproveRequestDTO) -> Dict[str, Any]:
        """Step 3: 결제 승인"""
        try:
            payment_data = {
                "merchant_uid": request.merchant_uid,
                "imp_uid": request.imp_uid,
            }
            result = await self.payment_service.approve_payment(payment_data)
            return dict(result)
        except PaymentValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
