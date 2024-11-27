from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.promotion_product.dtos.promotion_response import PromotionProductListResponse, PromotionProductResponse
from app.promotion_product.models.promotion_product import PromotionType
from app.promotion_product.services.promotion_services import PromotionProductService

router = APIRouter(prefix="/promotion-products", tags=["프로모션"])


@router.get("/get-list", response_model=PromotionProductListResponse)
async def get_promotion_products_route(
    promotion_type: str = Query(..., description="Promotion type: 'best' or 'md_pick'"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
) -> PromotionProductListResponse:
    if promotion_type not in ["best", "md_pick"]:
        raise HTTPException(status_code=400, detail="Invalid promotion type. Choose 'best' or 'md_pick'.")

    return await PromotionProductService.get_promotion_products(promotion_type, page, size)


@router.post("/add", response_model=PromotionProductResponse)
async def add_promotion(
    promotion_type: str = Query(..., description="Promotion type: 'best' or 'md_pick'"),
    is_active: bool = Query(..., description="True: active, False: inactive"),
    product_code: str = Query(..., description="Product code"),
) -> PromotionProductResponse:
    if promotion_type not in ["best", "md_pick"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid promotion type. Choose 'best' or 'md_pick'.",
        )

    if not product_code:
        raise HTTPException(
            status_code=400,
            detail="Product Code is required.",
        )

    return await PromotionProductService.add_promotion_products(promotion_type, is_active, product_code)


@router.patch("/update", response_model=PromotionProductResponse)
async def update_promotion(
    product_code: str,
    promotion_type: str,
    is_active: bool,
    new_promotion_type: Optional[PromotionType | None] = None,
    new_is_active: Optional[bool] = None,
) -> PromotionProductResponse:
    return await PromotionProductService.update_promotion_products(
        product_code, promotion_type, is_active, new_promotion_type, new_is_active
    )


@router.delete("/delete", response_model=None)
async def delete_promotion(product_code: str, promotion_type: str) -> None:
    return await PromotionProductService.delete_promotion_products(product_code, promotion_type)
