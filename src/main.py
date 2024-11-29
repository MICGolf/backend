import subprocess

from fastapi import FastAPI, Request

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
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    # Push 이벤트 및 develop 브랜치 확인
    if payload.get("ref") == "refs/heads/develop":
        # Git pull 명령 실행
        repo_path = "/path/to/your/repository"  # 서버의 레포지토리 경로
        try:
            subprocess.run(["git", "-C", repo_path, "pull", "origin", "develop"], check=True)
            return {"message": "Git pull executed successfully"}
        except subprocess.CalledProcessError as e:
            return {"error": f"Git pull failed: {e}"}

    return {"message": "No action taken"}
