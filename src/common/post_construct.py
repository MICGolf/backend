from fastapi import FastAPI

from common.handlers.exception_handler import attach_exception_handlers
from common.handlers.middleware_handler import attach_middleware_handlers
from common.handlers.router_handler import attach_router_handlers


def post_construct(app: FastAPI) -> None:
    attach_router_handlers(app)
    attach_exception_handlers(app=app)
    attach_middleware_handlers(app=app)
