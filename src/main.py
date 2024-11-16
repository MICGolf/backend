from fastapi import FastAPI

from common.handlers.middleware_handler import attach_middleware_handlers
from common.post_construct import post_construct

app = FastAPI()

attach_middleware_handlers(app=app)


async def startup_event() -> None:
    await post_construct(app=app)


app.add_event_handler("startup", startup_event)
