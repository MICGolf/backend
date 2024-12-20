from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from common.middlewares.access_token_middleware import AccessTokenMiddleware


def attach_middleware_handlers(app: FastAPI) -> None:
    origins = [
        "http://localhost:5173",
        "https://localhost:5173",
        "http://localhost:8000",
        "https://localhost:8000",
        "http://211.188.61.243:5173",
        "https://211.188.61.243:5173",
        "http://211.188.61.243:8000",
        "https://211.188.61.243:8000",
        "http://www.micgolf.shop/docs",
        "http://micgolf.kro.kr",
        "https://www.micgolf.shop/docs",
        "https://micgolf.kro.kr",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AccessTokenMiddleware)
    # app.add_middleware(CommonResponseMiddleware)
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=["micgolf.kro.kr", "*.micgolf.kro.kr", "localhost", "211.188.61.243", "test"],
    # )
