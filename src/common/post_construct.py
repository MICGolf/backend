from fastapi import FastAPI

from common.handlers.exception_handler import attach_exception_handlers
from common.handlers.router_handler import attach_router_handlers
from core.database.db_settings import database_initialize


async def post_construct(app: FastAPI) -> None:
    attach_router_handlers(app)
    attach_exception_handlers(app)
    await database_initialize(app)
