from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from core.configs import settings


TORTOISE_MODELS = [
    "app.banner.models.banner",
    "app.user.models.user",
    "app.cart.models.cart",
    "app.category.models.category",
    "app.order.models.order",
    "app.product.models.product",
    "app.promotion_product.models.promotion_product",
    "aerich.models",
]


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD,
                "database": settings.DB_NAME,
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
