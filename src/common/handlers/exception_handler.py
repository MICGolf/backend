from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.exceptions import DoesNotExist

from common.utils.logger import setup_logger
from core.configs import settings

logger = setup_logger("error_logger", settings=settings, enable_tortoise_logging=True)


def attach_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unexpected Error: {str(exc)} | Path: {request.url.path}", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "data": str(exc),
                "message": "An unexpected error occurred. Please try again later.",
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning(
            f"HTTPException: {exc.detail} | Path: {request.url.path} | Status: {exc.status_code}", exc_info=exc
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "data": exc.detail,
                "message": "An error occurred while processing your request.",
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Validation Error: {exc.errors()} | Path: {request.url.path}", exc_info=exc)
        error_messages = []
        for error in exc.errors():
            field = ".".join(map(str, error["loc"]))  # 필드 위치
            error_messages.append(f"{field}: {error['msg']}")

        # 새로운 에러 응답
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "errors": error_messages,  # 커스텀 에러 메시지 리스트
                "message": "Validation failed. Please check your input.",
            },
        )

    @app.exception_handler(DoesNotExist)
    async def does_not_exist_exception_handler(request: Request, exc: DoesNotExist) -> JSONResponse:
        logger.warning(f"DoesNotExist Error: {str(exc)} | Path: {request.url.path}", exc_info=exc)
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "data": str(exc),
                "message": "The requested resource does not exist.",
            },
        )

    @app.exception_handler(TypeError)
    async def type_error_exception_handler(request: Request, exc: TypeError) -> JSONResponse:
        logger.warning(f"Type Error: {str(exc)} | Path: {request.url.path}", exc_info=exc)
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "data": str(exc),
                "message": "A type error occurred while processing your request.",
            },
        )
