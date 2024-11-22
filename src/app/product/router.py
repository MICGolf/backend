import json

from fastapi import APIRouter, Body, Depends, File, Path, UploadFile, status

from app.product.dtos.request import (
    BatchUpdateStatusRequest,
    ProductFilterRequestDTO,
    ProductWithOptionCreateRequestDTO,
    ProductWithOptionUpdateRequestDTO,
)
from app.product.dtos.response import ProductResponseDTO
from app.product.example_schema.create_request_example import (
    PRODUCT_CREATE_DESCRIPTION,
    PRODUCT_CREATE_REQUEST_EXAMPLE_SCHEMA,
    PRODUCT_UPDATE_REQUEST_EXAMPLE_SCHEMA,
)
from app.product.services.product_service import ProductService
from common.utils.pagination_and_sorting_dto import PaginationAndSortingDTO
from core.configs import settings

router = APIRouter(prefix="/products", tags=["상품"])


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductResponseDTO,
    summary="상품 단일 조회 API",
    description="상품 단일 조회로 상품의 정보를 조회합니다",
)
async def get_product_handler(
    product_id: int = Path(..., description="조회할 상품의 ID"),
) -> ProductResponseDTO:
    return await ProductService.get_product_with_options(product_id=product_id)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[ProductResponseDTO],
    summary="상품 전체 조회 API",
    description="상품 전체 조회로 다양한 조건으로 필터링하여 조회가 가능합니다",
)
async def get_products_handler(
    filters: ProductFilterRequestDTO = Depends(),
    pagination_and_sorting: PaginationAndSortingDTO = Depends(),
) -> list[ProductResponseDTO]:
    return await ProductService.get_products_with_options(
        product_name=filters.product_name,
        product_id=filters.product_id,
        product_code=filters.product_code,
        sale_status=filters.sale_status,
        category_id=filters.category_id,
        start_date=filters.start_date,
        end_date=filters.end_date,
        page=pagination_and_sorting.page,
        page_size=pagination_and_sorting.page_size,
        sort=pagination_and_sorting.sort,
        order=pagination_and_sorting.order,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="상품 생성 API",
    description=PRODUCT_CREATE_DESCRIPTION,
)
async def create_products_handler(
    request: str = Body(
        media_type="application/json",
        examples=[
            PRODUCT_CREATE_REQUEST_EXAMPLE_SCHEMA,
        ],
    ),
    files: list[UploadFile] = File(...),
) -> None:
    request_data = json.loads(request)

    return await ProductService.create_product_with_options(
        product_create_dto=ProductWithOptionCreateRequestDTO(**request_data),
        files=files,
        upload_dir=settings.UPLOAD_DIR,
    )


@router.patch(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="상품 상태 업데이트 API",
    description="상품 상태를 업데이트합니다. status : 'Y' or 'N'",
)
async def update_products_status_handler(request: BatchUpdateStatusRequest) -> None:
    return await ProductService.update_products_status(product_ids=request.product_ids, status=request.status)


@router.patch(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="상품 업데이트 API",
    description="상품 업데이트",
)
async def update_product_handler(
    product_id: int = Path(..., description="수정할 상품의 ID"),
    request: str = Body(
        media_type="application/json",
        examples=[
            PRODUCT_UPDATE_REQUEST_EXAMPLE_SCHEMA,
        ],
    ),
    files: list[UploadFile] = File([]),
) -> None:
    request_data = json.loads(request)

    return await ProductService.update_product_with_options(
        product_id=product_id,
        product_update_dto=ProductWithOptionUpdateRequestDTO(**request_data),
        files=files,
        upload_dir=settings.UPLOAD_DIR,
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="상품 삭제 API",
    description="단일 상품 삭제",
)
async def delete_product_handler(
    product_id: int = Path(..., description="삭제할 상품의 ID"),
) -> None:
    return await ProductService.delete_product(product_id=product_id)
