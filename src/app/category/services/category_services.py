from typing import Any, List, Optional, Union

from fastapi import HTTPException
from tortoise.expressions import Q
from tortoise.functions import Count

from app.category.dtos.category_request import (
    CategoryChildRequest,
    CategoryCreateRequest,
    CategoryCreateTreeRequest,
    CategoryUpdateRequest,
)
from app.category.dtos.category_response import (
    CategoryResponse,
    CategoryTreeResponse,
    CategoryWithSubcategoriesResponse,
)
from app.category.models.category import Category


class CategoryService:
    @staticmethod
    async def get_categories(page: int, limit: int, parent_id: Optional[int] = None) -> List[CategoryResponse]:
        skip = (page - 1) * limit
        categories = await Category.filter(parent_id=parent_id if parent_id else None).offset(skip).limit(limit)
        return [CategoryResponse.model_validate(category, from_attributes=True) for category in categories]

    @staticmethod
    async def get_category_detail(category_id: int) -> CategoryResponse:
        category = await Category.get_or_none(id=category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        return CategoryResponse.model_validate(category, from_attributes=True)

    @staticmethod
    async def create_category(request: CategoryCreateRequest) -> CategoryResponse:
        # 같은 부모 카테고리 내에서 이름 중복 체크 추가
        exists = await Category.filter(name=request.name, parent_id=request.parent_id).exists()
        if exists:
            raise HTTPException(status_code=400, detail="이미 존재하는 이름입니다.")

        depth = 0
        if request.parent_id:
            parent = await Category.get_or_none(id=request.parent_id)
            if not parent:
                raise HTTPException(status_code=404, detail="부모카테고리가 존재하지 않습니다.")
            # 최대 depth 제한 추가
            if parent.depth >= 3:  # 예: 최대 3단계까지만 허용
                raise HTTPException(
                    status_code=400,
                    detail="카테고리는 최대 대분류, 중분류, 소분류까지로 나눌 수 있습니다.",
                )
            depth = parent.depth + 1

        category = await Category.create(name=request.name, parent_id=request.parent_id, depth=depth)
        return CategoryResponse.model_validate(category, from_attributes=True)

    @staticmethod
    async def update_category(category_id: int, request: CategoryUpdateRequest) -> CategoryResponse:
        category = await Category.get_or_none(id=category_id)
        if not category:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")

        update_data = request.model_dump(exclude_unset=True)

        if request.parent_id and request.parent_id == category_id:
            raise HTTPException(status_code=400, detail="부모카테고리는 본인이 될 수 없습니다.")

            # 이름 변경 시 중복 체크
        if request.name:
            exists = await Category.filter(name=request.name, parent_id=request.parent_id, id__not=category_id).exists()
            if exists:
                raise HTTPException(
                    status_code=400,
                    detail="부모 카테고리 내에 중복되는 이름이 존재합니다.",
                )

        if "parent_id" in update_data:
            if update_data["parent_id"]:
                parent = await Category.get_or_none(id=update_data["parent_id"])
                if not parent:
                    raise HTTPException(status_code=404, detail="부모 카테고리를 찾을 수 없습니다.")
                update_data["depth"] = parent.depth + 1
            else:
                update_data["depth"] = 0

        await category.update_from_dict(update_data).save()
        await category.refresh_from_db()
        return CategoryResponse.model_validate(category, from_attributes=True)

    @staticmethod
    async def delete_category(category_id: int) -> None:
        # 카테고리와 하위 카테고리 한번에 조회
        category = await Category.get_or_none(id=category_id).prefetch_related("subcategory", "category_product")
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        # 현재 카테고리와 하위 카테고리들의 ID 수집
        subcategory_ids = [category.id]
        subcategories = await category.subcategory.all()  # type: ignore
        subcategory_ids.extend([sub.id for sub in subcategories])

        # 모든 연관된 카테고리의 상품 연결 여부를 한번에 확인
        categories_with_products = (
            await Category.filter(id__in=subcategory_ids)
            .annotate(product_count=Count("category_product"))
            .values("id", "name", "product_count")
        )

        # 연결된 상품이 있는지 확인
        for cat in categories_with_products:
            if cat["product_count"] > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Category {cat['name']} has linked products",
                )

        # 모든 연관 카테고리 삭제
        await category.delete()

    @staticmethod
    async def get_category_and_subcategories(category_id: int) -> list[tuple[Any, ...]]:
        return await Category.filter(Q(id=category_id) | Q(parent_id=category_id)).values_list("id", flat=True)

    @staticmethod
    async def get_category_with_ancestors(category_id: int) -> dict[str, Any]:
        category = await Category.get_or_none(id=category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        ancestors = []
        current = category
        while current.parent:
            parent = await Category.get(id=current.parent)
            ancestors.append(CategoryResponse.model_validate(parent, from_attributes=True))
            current = parent

        # 대분류부터 순서대로 정렬
        ancestors.reverse()

        return {
            "category": CategoryResponse.model_validate(category, from_attributes=True),
            "ancestors": ancestors,
        }

    @staticmethod
    async def create_category_tree(
        request: CategoryCreateTreeRequest,
    ) -> List[CategoryTreeResponse]:
        async def create_tree(
            data: Union[CategoryCreateTreeRequest, CategoryChildRequest],
            parent_id: Optional[int] = None,
            depth: int = 0,
        ) -> Category:
            # 현재 카테고리 생성
            category = await Category.create(name=data.name, parent_id=parent_id, depth=depth)

            # 하위 카테고리들 생성
            if data.children:
                for child in data.children:
                    await create_tree(child, category.pk, depth + 1)

            return category

        root = await create_tree(request)
        # 생성 완료 후 전체 트리 조회
        categories = await Category.filter(parent_id=None).prefetch_related("subcategory")

        async def build_response_tree(category: Category) -> CategoryTreeResponse:
            subcategories: List[Category] = await Category.filter(parent_id=category.pk)
            return CategoryTreeResponse(
                id=category.pk,
                name=category.name,
                depth=category.depth,
                created_at=category.created_at,
                updated_at=category.updated_at,
                children=[await build_response_tree(sub) for sub in subcategories],
            )

        return [await build_response_tree(cat) for cat in categories]
