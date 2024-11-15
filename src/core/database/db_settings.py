import os

from fastapi import FastAPI

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv

# 환경변수 .env 로드
load_dotenv()

TORTOISE_MODELS = [
    "src.app.banner.models.banner",
    "src.app.best_production.models.best_production",
    "src.app.category.models.category",
    "src.app.mds_choice.models.mds_choice",
    "src.app.product.models.product",
    "aerich.models",
]

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": os.getenv("DB_HOST", "127.0.0.1"),
                "port": int(os.getenv("DB_PORT", 3306)),
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME"),
                "connect_timeout": 5,
                # "maxsize": configs.MAX_CONNECTION_PER_CONNECTION_POOL,
            },
        },
    },
    "apps": {
        "models": {
            "models": TORTOISE_MODELS,
        },
    },
    # "routers": ["app.configs.database_config.Router"],
    "timezone": "Asia/Seoul",
}


async def database_initialize(app: FastAPI) -> None:
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        register_tortoise(
            app,
            config=TORTOISE_ORM,
            generate_schemas=False,
            add_exception_handlers=True,
        )
    except Exception as e:
        print(f"Database initialization failed: {e}")

