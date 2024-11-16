from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


def attach_middleware_handlers(app: FastAPI) -> None:
    origins = [
        "http://localhost:5173",
        "https://localhost:5173",
        "http://111.111.111.111:8000",  # 특정 포트 포함
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
