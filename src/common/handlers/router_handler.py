from fastapi import FastAPI

from app.banner.router import router as banner_router
from app.best_production.router import router as best_product_router
from app.category.router import router as category_router
from app.mds_choice.router import router as mds_choice_router
from app.product.router import router as product_router


def attach_router_handlers(app: FastAPI) -> None:
    app.include_router(router=product_router, prefix="/api/v1")
    app.include_router(router=banner_router, prefix="/api/v1")
    app.include_router(router=category_router, prefix="/api/v1")
    app.include_router(router=mds_choice_router, prefix="/api/v1")
    app.include_router(router=best_product_router, prefix="/api/v1")
