from fastapi import APIRouter, HTTPException, Query

from app.promotion_product.dtos.promotion_response import PromotionProductListResponse
from app.promotion_product.services.promotion_services import PromotionProductService

router = APIRouter(prefix="/promotion-products", tags=["프로모션"])


@router.get("", response_model=PromotionProductListResponse)
async def get_promotion_products_route(
    promotion_type: str = Query(..., description="Promotion type: 'best' or 'md_pick'"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
) -> PromotionProductListResponse:
    if promotion_type not in ["best", "md_pick"]:
        raise HTTPException(status_code=400, detail="Invalid promotion type. Choose 'best' or 'md_pick'.")

    return await PromotionProductService.get_promotion_products(promotion_type, page, size)
