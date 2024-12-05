from typing import Any, Dict, Optional

from fastapi import HTTPException


class PaymentException(HTTPException):
    """기본 결제 예외 클래스"""

    def __init__(
        self,
        status_code: int = 400,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class PaymentValidationError(PaymentException):
    """결제 데이터 검증 실패"""

    def __init__(self, detail: str = "결제 데이터가 유효하지 않습니다") -> None:
        super().__init__(status_code=400, detail=detail)


class PaymentProcessError(PaymentException):
    """결제 처리 실패"""

    def __init__(self, detail: str = "결제 처리 중 오류가 발생했습니다") -> None:
        super().__init__(status_code=500, detail=detail)


class PaymentNotFoundError(PaymentException):
    """결제 정보 없음"""

    def __init__(self, detail: str = "결제 정보를 찾을 수 없습니다") -> None:
        super().__init__(status_code=404, detail=detail)


class PaymentStatusError(PaymentException):
    """잘못된 결제 상태"""

    def __init__(self, detail: str = "잘못된 결제 상태입니다") -> None:
        super().__init__(status_code=400, detail=detail)


class PortoneAPIError(PaymentException):
    """포트원 API 오류"""

    def __init__(self, detail: str = "포트원 API 호출 중 오류가 발생했습니다") -> None:
        super().__init__(status_code=500, detail=detail)


class PaymentMethodError(PaymentException):
    """결제 수단 오류"""

    def __init__(self, detail: str = "지원하지 않는 결제 수단입니다") -> None:
        super().__init__(status_code=400, detail=detail)


class PGProviderError(PaymentException):
    """PG사 오류"""

    def __init__(self, detail: str = "지원하지 않는 PG사입니다") -> None:
        super().__init__(status_code=400, detail=detail)
