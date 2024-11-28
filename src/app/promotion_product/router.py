from fastapi import APIRouter, HTTPException, Query

from app.promotion_product.dtos.promotion_request import (
    AddPromotionRequest,
    DeletePromotionRequest,
    UpdatePromotionRequest,
)
from app.promotion_product.dtos.promotion_response import PromotionProductListResponse, PromotionProductResponse
from app.promotion_product.services.promotion_services import PromotionProductService

router = APIRouter(prefix="/promotion-products", tags=["프로모션"])


@router.get("/get-list", response_model=PromotionProductListResponse)
async def get_promotion_products_route(
    promotion_type: str = Query(..., description="Promotion type: 'best' or 'md_pick'"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
) -> PromotionProductListResponse:
    return await PromotionProductService.get_promotion_products(promotion_type, page, size)


@router.post("/add", response_model=PromotionProductResponse)
async def add_promotion(request: AddPromotionRequest) -> PromotionProductResponse:
    return await PromotionProductService.add_promotion_products(request)


@router.patch("/update", response_model=PromotionProductResponse)
async def update_promotion(request: UpdatePromotionRequest) -> PromotionProductResponse:
    return await PromotionProductService.update_promotion_products(request)


@router.delete("/delete", response_model=None)
async def delete_promotion(request: DeletePromotionRequest) -> None:
    return await PromotionProductService.delete_promotion_products(request)
