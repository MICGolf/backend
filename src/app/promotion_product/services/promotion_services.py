from typing import Optional

from fastapi import HTTPException
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
            "product",  # PromotionProduct와 연결된 Product 객체를 미리 가져옵니다.
            "product__options",  # Product와 연결된 Option 객체들을 미리 가져옵니다.
            "product__options__images",  # Option과 연결된 OptionImage 객체들을 미리 가져옵니다.
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
                        "product_code": item.product.product_code,
                        "product_name": item.product.name,
                        "price": item.product.price,
                        "promotion_type": item.promotion_type,
                        "is_active": item.is_active,
                        "image_url": (
                            item.product.options[0].images[0].image_url
                            if item.product.options and item.product.options[0].images
                            else ""
                        ),
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
        product_code: str,
    ) -> PromotionProductResponse:
        """프로모션 추가 기능"""
        # 제품 코드로 제품 조회
        # options와 images 관계를 미리 로드
        product = await Product.filter(product_code=product_code).prefetch_related("options", "options__images").first()
        if not product:
            raise DoesNotExist(f"Product with code '{product_code}' does not exist.")
        product_id = product.id

        # 기존 프로모션 검색
        existing_promotion = await PromotionProduct.filter(product_id=product_id, promotion_type=promotion_type).first()

        # 이미 프로모션이 존재하는 경우
        if existing_promotion:
            existing_promotion.is_active = is_active
            await existing_promotion.save()
            promotion = existing_promotion
        else:
            # 기존에 프로모션이 존재하지 않는 경우
            promotion = await PromotionProduct.create(
                promotion_type=promotion_type,
                is_active=is_active,
                product_id=product_id,
            )

        # 생성된 프로모션 가져오기
        return PromotionProductResponse.model_validate(
            {
                "id": promotion.id,
                "product_code": product.product_code,
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "promotion_type": promotion.promotion_type,
                "is_active": promotion.is_active,
                "image_url": (
                    product.options[0].images[0].image_url if product.options and product.options[0].images else ""
                ),
            },
            from_attributes=True,
        )

    @staticmethod
    async def update_promotion_products(
        product_code: str,
        promotion_type: str,
        is_active: bool,
        new_promotion_type: Optional[PromotionType | None] = None,
        new_is_active: Optional[bool] = None,
    ) -> PromotionProductResponse:
        """프로모션 업데이트"""
        # 제품 코드로 제품 조회 (options와 images 관계를 미리 로드)
        product = await Product.filter(product_code=product_code).prefetch_related("options", "options__images").first()
        if not product:
            raise DoesNotExist(f"{product_code}는 존재하지 않는 상품코드 입니다.")

        # 해당 제품의 프로모션 조회
        promotion = await PromotionProduct.filter(
            product_id=product.id, promotion_type=promotion_type, is_active=is_active
        ).first()

        if not promotion:
            raise HTTPException(
                status_code=404,
                detail=f"{product_code}의 {promotion_type}은 등록되어 있지 않은 프로모션입니다.",
            )

        # new_promotion_type이 제공된 경우 해당 값을 반영
        if new_promotion_type:
            promotion.promotion_type = new_promotion_type

        # new_is_active가 제공된 경우 해당 값을 반영
        if new_is_active is not None:
            promotion.is_active = new_is_active

        # 업데이트 저장
        await promotion.save()

        # 업데이트된 값을 PromotionProductResponse로 반환
        return PromotionProductResponse.model_validate(
            {
                "id": promotion.id,
                "product_code": product.product_code,
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "promotion_type": promotion.promotion_type,
                "is_active": promotion.is_active,
                "image_url": (
                    product.options[0].images[0].image_url if product.options and product.options[0].images else ""
                ),
            },
            from_attributes=True,
        )

    @staticmethod
    async def delete_promotion_products(product_code: str, promotion_type: str) -> None:
        """프로모션 삭제"""
        product = await Product.get(product_code=product_code)
        deleted_count = await PromotionProduct.filter(product_id=product.id, promotion_type=promotion_type).delete()
        if deleted_count == 0:
            raise DoesNotExist(
                f"No PromotionProduct found with product_code={product_code}, promotion_type={promotion_type}"
            )
