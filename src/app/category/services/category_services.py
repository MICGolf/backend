# app/category/services/category_service.py
from typing import List, Optional

from fastapi import HTTPException

from app.category.dtos.category_request import CategoryCreateRequest, CategoryUpdateRequest
from app.category.dtos.category_response import CategoryResponse, CategoryWithSubcategoriesResponse
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
        depth = 0
        if request.parent_id:
            parent = await Category.get_or_none(id=request.parent_id)
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")
            depth = parent.depth + 1

        category = await Category.create(name=request.name, parent_id=request.parent_id, depth=depth)
        return CategoryResponse.model_validate(category, from_attributes=True)

    @staticmethod
    async def update_category(category_id: int, request: CategoryUpdateRequest) -> CategoryResponse:
        category = await Category.get_or_none(id=category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        update_data = request.model_dump(exclude_unset=True)

        if "parent_id" in update_data:
            if update_data["parent_id"]:
                parent = await Category.get_or_none(id=update_data["parent_id"])
                if not parent:
                    raise HTTPException(status_code=404, detail="Parent category not found")
                update_data["depth"] = parent.depth + 1
            else:
                update_data["depth"] = 0

        await category.update_from_dict(update_data).save()
        await category.refresh_from_db()
        return CategoryResponse.model_validate(category, from_attributes=True)

    @staticmethod
    async def delete_category(category_id: int) -> None:
        category = await Category.get_or_none(id=category_id).prefetch_related("subcategory", "category_product")
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if await category.subcategory.all().count() > 0:  # type: ignore
            raise HTTPException(status_code=400, detail="Cannot delete category with subcategories")

        if await category.category_product.all().count() > 0:  # type: ignore
            raise HTTPException(status_code=400, detail="Cannot delete category with products")

        await category.delete()
