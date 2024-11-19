from fastapi import FastAPI

from common.handlers.middleware_handler import attach_middleware_handlers
from common.post_construct import post_construct
from common.utils.logger import setup_logger
from core.configs import settings

app_logger = setup_logger("my_app_logger", settings=settings, enable_tortoise_logging=True)

app = FastAPI()

attach_middleware_handlers(app=app)


async def startup_event() -> None:
    await post_construct(app=app)


app.add_event_handler("startup", startup_event)
