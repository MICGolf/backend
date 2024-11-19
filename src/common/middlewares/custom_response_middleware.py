from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import json


class CommonResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):

        # 요청 처리 및 응답 받기
        response = await call_next(request)

        if request.url.path.startswith(("/docs", "/openapi.json")):
            return await call_next(request)

        if isinstance(response, (StreamingResponse, type(response))):
            body = b"".join([chunk async for chunk in response.body_iterator])
            response.body_iterator = iter([body])

            try:
                data = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                data = body.decode("utf-8")

            return JSONResponse(
                content={
                    "code": response.status_code,
                    "data": data,
                    "message": "정상 처리되었습니다." if response.status_code == 200 else "오류가 발생했습니다.",
                },
                status_code=response.status_code,
            )

        return response
