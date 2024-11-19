import json
from typing import Awaitable, Callable

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse


class CommonResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:

        # 요청 처리 및 응답 받기
        response = await call_next(request)

        if request.url.path.startswith(("/docs", "/openapi.json")):
            return response

        if response.status_code >= 400:
            return response

        if isinstance(response, (StreamingResponse, type(response))):
            body = b"".join([chunk async for chunk in response.body_iterator])  # type: ignore[attr-defined]
            response.body_iterator = iter([body])  # type: ignore[attr-defined]

            try:
                data = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                data = body.decode("utf-8")

            return JSONResponse(
                content={
                    "code": response.status_code,
                    "data": data,
                    "message": "정상 처리되었습니다.",
                },
                status_code=response.status_code,
            )

        return response
