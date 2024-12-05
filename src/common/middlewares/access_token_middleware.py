from typing import Awaitable, Callable, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.user.dtos.auth_dto import JwtPayloadTypedDict
from app.user.services.auth_service import AuthenticateService
from common.exceptions.custom_exceptions import AccessTokenExpiredException
from common.exceptions.error_code import ErrorCode


class AccessTokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self.auth_service = AuthenticateService()

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        authorization: Optional[str] = request.headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            return await call_next(request)

        token = authorization.split(" ")[1]

        payload: JwtPayloadTypedDict = self.auth_service._decode_token(token)

        if not self.auth_service.is_valid_access_token(payload):
            return JSONResponse(
                status_code=401,
                content={
                    "code": 401,
                    "data": None,
                    "message": str(ErrorCode.ACCESS_TOKEN_EXPIRED.value[1]),
                },
            )

        request.state.user = {
            "user_id": payload["user_id"],
            "user_type": payload["user_type"],
        }

        response = await call_next(request)
        return response
