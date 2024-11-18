# app/category/routes/category_router.py
from typing import List, Optional

from fastapi import APIRouter, Path, Query

from app.category.dtos.category_request import CategoryCreateRequest, CategoryUpdateRequest
from app.category.dtos.category_response import CategoryResponse
from app.category.services.category_services import CategoryService

router = APIRouter(prefix="/category", tags=["카테고리"])


@router.get("", response_model=List[CategoryResponse], summary="카테고리 목록 조회")
async def get_categories(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    parent_id: Optional[int] = Query(None, description="상위 카테고리 ID"),
) -> List[CategoryResponse]:
    return await CategoryService.get_categories(page, limit, parent_id)


@router.get("/{category_id}", response_model=CategoryResponse, summary="카테고리 상세 조회")
async def get_category(category_id: int = Path(..., description="카테고리 ID")) -> CategoryResponse:
    return await CategoryService.get_category_detail(category_id)


@router.post("", response_model=CategoryResponse, status_code=201, summary="카테고리 생성")
async def create_category(request: CategoryCreateRequest) -> CategoryResponse:
    return await CategoryService.create_category(request)


@router.put("/{category_id}", response_model=CategoryResponse, summary="카테고리 수정")
async def update_category(
    request: CategoryUpdateRequest,
    category_id: int = Path(..., description="카테고리 ID"),
) -> CategoryResponse:
    return await CategoryService.update_category(category_id, request)


@router.delete("/{category_id}", status_code=204, summary="카테고리 삭제")
async def delete_category(category_id: int = Path(..., description="카테고리 ID")) -> None:
    await CategoryService.delete_category(category_id)
