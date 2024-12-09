from fastapi import FastAPI

from app.banner.router import router as banner_router
from app.cart.router import router as cart_router
from app.category.router import router as category_router
from app.order.router import router as order_router
from app.order.router_payment import router as payment_router
from app.product.router import router as product_router
from app.promotion_product.router import router as promotion_product_router
from app.user.router_auth import router as auth_router
from app.user.router_oauth import router as oauth_router
from common.github_webhook.github_webhook import router as github_router


def attach_router_handlers(app: FastAPI) -> None:
    app.include_router(router=product_router, prefix="/api/v1")
    app.include_router(router=banner_router, prefix="/api/v1")
    app.include_router(router=category_router, prefix="/api/v1")
    app.include_router(router=promotion_product_router, prefix="/api/v1")
    app.include_router(router=cart_router, prefix="/api/v1")
    app.include_router(router=order_router, prefix="/api/v1")
    app.include_router(router=auth_router, prefix="/api/v1")
    app.include_router(router=oauth_router, prefix="/api/v1")
    app.include_router(router=payment_router, prefix="/api/v1")
    app.include_router(router=github_router, prefix="/webhook")
