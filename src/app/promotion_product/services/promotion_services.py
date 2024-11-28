from fastapi import HTTPException
from tortoise.expressions import Q

from app.product.models.product import Product
from app.promotion_product.dtos.promotion_request import (
    AddPromotionRequest,
    DeletePromotionRequest,
    UpdatePromotionRequest,
)
from app.promotion_product.dtos.promotion_response import PromotionProductListResponse, PromotionProductResponse
from app.promotion_product.models.promotion_product import PromotionProduct, PromotionType


class PromotionProductService:
    @staticmethod
    async def get_promotion_products(
        promotion_type: str, page: int = 1, size: int = 10
    ) -> PromotionProductListResponse:
        """프로모션 조회"""
        skip = (page - 1) * size
        query = PromotionProduct.filter(Q(promotion_type=promotion_type) & Q(is_active=True)).prefetch_related(
            "product", "product__options", "product__options__images"
        )
        total = await query.count()
        items = await query.offset(skip).limit(size)

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
    async def add_promotion_products(request: AddPromotionRequest) -> PromotionProductResponse:
        product = (
            await Product.filter(product_code=request.product_code)
            .prefetch_related("options", "options__images")
            .first()
        )
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with code '{request.product_code}' does not exist.")
        product_id = product.id
        existing_promotion = await PromotionProduct.filter(
            product_id=product_id, promotion_type=request.promotion_type
        ).first()

        if existing_promotion:
            existing_promotion.is_active = request.is_active
            await existing_promotion.save()
            promotion = existing_promotion
        else:
            promotion = await PromotionProduct.create(
                promotion_type=request.promotion_type,
                is_active=request.is_active,
                product_id=product_id,
            )

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
    async def update_promotion_products(request: UpdatePromotionRequest) -> PromotionProductResponse:
        product = (
            await Product.filter(product_code=request.product_code)
            .prefetch_related("options", "options__images")
            .first()
        )
        if not product:
            raise HTTPException(status_code=404, detail=f"{request.product_code}는 존재하지 않는 상품코드 입니다.")
        promotion = await PromotionProduct.filter(
            product_id=product.id, promotion_type=request.promotion_type, is_active=request.is_active
        ).first()

        if not promotion:
            raise HTTPException(
                status_code=404,
                detail=f"{request.product_code}의 {request.promotion_type}은 등록되어 있지 않은 프로모션입니다.",
            )

        # new_promotion_type이 제공된 경우 해당 값을 반영
        if request.new_promotion_type:
            promotion.promotion_type = PromotionType(request.new_promotion_type)

        if request.new_is_active is not None:
            promotion.is_active = request.new_is_active

        await promotion.save()

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
    async def delete_promotion_products(request: DeletePromotionRequest) -> None:
        product = await Product.filter(product_code=request.product_code).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with code '{request.product_code}' does not exist.")
        deleted_count = await PromotionProduct.filter(
            product_id=product.id, promotion_type=request.promotion_type
        ).delete()
        if deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No PromotionProduct found with product_code={request.product_code}, "
                f"promotion_type={request.promotion_type}",
            )
