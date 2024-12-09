from pydantic import BaseModel, Field


class PaymentReserveResponseDTO(BaseModel):
    """결제 예약 요청 DTO"""

    payment_id: str = Field(..., description="결제 ID")

    @classmethod
    async def build(cls, payment_id: str) -> "PaymentReserveResponseDTO":
        return cls(payment_id=payment_id)
