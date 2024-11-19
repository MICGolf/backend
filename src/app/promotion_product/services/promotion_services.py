from typing import Any, Dict, List, Optional

from tortoise.expressions import Q

from app.promotion_product.dtos.promotion_response import PromotionProductListResponse, PromotionProductResponse
from app.promotion_product.models.promotion_product import PromotionProduct


class PromotionProductService:
    @staticmethod
    async def get_promotion_products(
        promotion_type: str, page: int = 1, size: int = 10
    ) -> dict[str, int | list[dict[str, Any]]]:
        # 페이지네이션 계산
        skip = (page - 1) * size

        # 쿼리 구성
        query = PromotionProduct.filter(Q(promotion_type=promotion_type) & Q(is_active=True)).prefetch_related(
            "product"
        )

        # 총 개수와 아이템 목록을 가져옴
        total = await query.count()
        items = await query.offset(skip).limit(size)

        # 응답을 PromotionProductResponse 모델로 반환
        return {
            "items": [PromotionProductResponse.model_validate(item, from_attributes=True).dict() for item in items],
            "total": total,
            "page": page,
            "size": size,
        }