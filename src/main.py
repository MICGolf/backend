from fastapi import FastAPI

from common.post_construct import post_construct

app = FastAPI()


async def startup_event() -> None:
    await post_construct(app=app)


app.add_event_handler("startup", startup_event)
