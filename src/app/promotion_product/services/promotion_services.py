from typing import Any, Dict, List, Optional

from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from app.product.models.product import Product
from app.promotion_product.dtos.promotion_response import PromotionProductListResponse, PromotionProductResponse
from app.promotion_product.models.promotion_product import PromotionProduct, PromotionType


class PromotionProductService:
    @staticmethod
    async def get_promotion_products(
        promotion_type: str, page: int = 1, size: int = 10
    ) -> PromotionProductListResponse:
        """프로모션 조회"""
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
        return PromotionProductListResponse(
            items=[
                PromotionProductResponse.model_validate(
                    {
                        "id": item.id,
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "price": item.product.price,
                        "promotion_type": item.promotion_type,
                        "is_active": item.is_active,
                    },
                    from_attributes=True,
                )
                for item in items
            ],
            total=total,
            page=page,
            size=size,
        )

    @staticmethod
    async def add_promotion_products(
        promotion_type: str,
        is_active: bool,
        product_name: str,
    ) -> PromotionProductResponse:
        # 제품 이름으로 제품 조회
        product = await Product.get(name=product_name)
        product_id = product.id

        # 프로모션 생성
        create_promotion = await PromotionProduct.create(
            promotion_type=promotion_type,
            is_active=is_active,
            product_id=product_id,
        )

        # 생성된 프로모션 가져오기
        promotion = await PromotionProduct.get(id=create_promotion.id).prefetch_related("product")
        return PromotionProductResponse.model_validate(
            {
                "id": promotion.id,
                "product_id": promotion.product.id,
                "product_name": promotion.product.name,
                "price": promotion.product.price,
                "promotion_type": promotion.promotion_type,
                "is_active": promotion.is_active,
            },
            from_attributes=True,
        )

    @staticmethod
    async def update_promotion_products(
        product_id: int,
        promotion_type: str,
        is_active: bool,
        new_promotion_type: Optional[PromotionType | None] = None,
        new_is_active: Optional[bool] = None,
    ) -> PromotionProductResponse:
        """프로모션 업데이트"""
        try:
            # 해당 상품과 프로모션 타입으로 목표 상품 가져오기
            update_query = await PromotionProduct.get(
                product_id=product_id, promotion_type=promotion_type, is_active=is_active
            ).prefetch_related("product")

            # new_promotion_type이 제공된 경우 해당 값을 반영
            if new_promotion_type:
                update_query.promotion_type = new_promotion_type

            # new_is_active가 제공된 경우 해당 값을 반영
            if new_is_active is not None:
                update_query.is_active = new_is_active

            # 업데이트 저장
            await update_query.save()

            # 업데이트된 값을 PromotionProductResponse로 반환
            return PromotionProductResponse.model_validate(
                {
                    "id": update_query.id,
                    "product_id": update_query.product.id,
                    "product_name": update_query.product.name,
                    "price": update_query.product.price,
                    "promotion_type": update_query.promotion_type,
                    "is_active": update_query.is_active,
                },
                from_attributes=True,
            )
        except DoesNotExist:
            raise DoesNotExist(
                f"No PromotionProduct found with product_id={product_id}, promotion_type={promotion_type}"
            )

    @staticmethod
    async def delete_promotion_products(product_id: int, promotion_type: str) -> None:
        """프로모션 삭제"""
        obj_query = await PromotionProduct.get(product_id=product_id, promotion_type=promotion_type)
        # 프로모션의 상태를 원하는 상태로 변경

        await obj_query.delete()
