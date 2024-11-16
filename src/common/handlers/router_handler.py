from fastapi import FastAPI

from app.banner.router import router as banner_router
from app.cart.router import router as cart_router
from app.category.router import router as category_router
from app.order.router import router as order_router
from app.product.router import router as product_router
from app.promotion_product.router import router_best, router_mds
from app.user.router import router as user_router


def attach_router_handlers(app: FastAPI) -> None:
    app.include_router(router=product_router, prefix="/api/v1")
    app.include_router(router=banner_router, prefix="/api/v1")
    app.include_router(router=category_router, prefix="/api/v1")
    app.include_router(router=router_best, prefix="/api/v1")
    app.include_router(router=router_mds, prefix="/api/v1")
    app.include_router(router=user_router, prefix="/api/v1")
    app.include_router(router=cart_router, prefix="/api/v1")
    app.include_router(router=order_router, prefix="/api/v1")
