from fastapi import FastAPI

from common.post_construct import post_construct
from common.utils.logger import setup_logger
from core.configs import settings
from core.database.db_settings import database_initialize

logger = setup_logger("my_app_logger", settings=settings, enable_tortoise_logging=True)

app = FastAPI()


async def startup_event() -> None:
    await database_initialize(app)


post_construct(app=app)

app.add_event_handler("startup", startup_event)


@app.get("/health-check")
async def health_check():
    return {"status": "ok"}
