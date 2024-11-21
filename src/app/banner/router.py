from fastapi import APIRouter, Depends, File, Form, Path, Query, UploadFile

from app.banner.dtos.request import BannerCreateRequest, BannerUpdateRequest
from app.banner.dtos.response import BannerListResponse, BannerResponse
from app.banner.services.banner_service import BannerService
from common.utils.pagination_and_sorting_dto import PaginationAndSortingDTO

# 배너 관리를 위한 라우터
router = APIRouter(prefix="/banners", tags=["배너"])


@router.get(
    "/",
    response_model=BannerListResponse,
    summary="배너 목록 조회",
    description="배너 또는 프로모션 목록을 페이지네이션하여 조회합니다.",
)
async def get_banners(
    query: str | None = Query(
        None,
        title="조회할 타입",
        description="배너 타입 필터링 (미입력 시 전체 조회)",
        regex="^(banner|promotion)$",
        example="banner",
    ),
    pagination: PaginationAndSortingDTO = Depends(),
) -> BannerListResponse:
    """배너 목록 조회

    정렬 순서:
    1. 카테고리 타입
    2. 표시 순서
    3. 생성일시

    - 정렬 필드: created_at, display_order, title
    - 정렬 방향: asc(오름차순), desc(내림차순)
    - 페이지 크기: 1-100
    """
    return await BannerService.get_banners(query_type=query, pagination=pagination)


@router.post(
    "/",
    response_model=BannerResponse,
    summary="배너 생성",
    description="새로운 배너를 생성합니다. 이미지는 1920x1080px JPG 형식만 가능합니다.",
)
async def create_banner(
    title: str = Form(..., title="배너 제목", description="배너 제목", example="리코브랜드"),
    subTitle: str = Form(..., title="배너 소제목", description="배너 소제목", example="이번달 할인상품 총 모음전"),
    eventUrl: str = Form(
        ..., title="이벤트 URL", description="클릭시 이동할 이벤트 URL", example="https://example.com/event"
    ),
    banner_type: str = Form(..., title="배너 타입", description="banner 또는 promotion", example="banner"),
    is_active: bool = Form(True, title="활성화 상태", description="배너 활성화 상태 (기본값: True)", example=True),
    image: UploadFile = File(..., title="배너 이미지", description="JPG 형식의 이미지"),
) -> BannerResponse:
    """
    새로운 배너를 생성합니다.

    - **title**: 배너 제목 (필수)
    - **subTitle**: 배너 소제목 (필수)
    - **eventUrl**: 클릭시 이동할 이벤트 URL (필수)
    - **banner_type**: 배너 타입 (banner/promotion) (필수)
    - **is_active**: 활성화 상태 (기본값: True)
    - **image**: 배너 이미지 (1920x1080px JPG) (필수)
    """
    request = BannerCreateRequest(
        title=title, subTitle=subTitle, eventUrl=eventUrl, banner_type=banner_type, is_active=is_active
    )
    return await BannerService.create_banner(request, image)


@router.patch(
    "/{banner_id}",
    response_model=BannerResponse,
    description="기존 배너의 정보를 수정합니다. 수정하지 않을 필드는 생략 가능합니다.",
)
async def update_banner(
    banner_id: int = Path(..., description="수정할 배너의 ID"),
    title: str | None = Form(None, description="수정할 배너 제목", example="수정된 리코브랜드"),
    sub_title: str | None = Form(None, description="수정할 배너 소제목", example="수정된 할인상품 모음전"),
    event_url: str | None = Form(None, description="수정할 이벤트 URL", example="https://example.com/event-updated"),
    category_type: str | None = Form(None, description="수정할 배너 타입 (banner/promotion)", example="promotion"),
    is_active: bool | None = Form(None, description="수정할 활성화 상태", example=False),
    display_order: int | None = Form(None, description="수정할 표시 순서 (0부터 시작)", example=1),
    image: UploadFile | None = File(None, description="정할 배너 이미지 (JPG 형식)"),
) -> BannerResponse:
    """
    배너 수정

    - 수정하지 않을 필드는 생략 가능
    - 이미지 수정 시 1920x1080px JPG 형식만 가능
    - 카테고리 타입 변경 시 표시 순서 자동 조정
    """
    request = BannerUpdateRequest(
        title=title,
        sub_title=sub_title,
        event_url=event_url,
        category_type=category_type,
        is_active=is_active,
        display_order=display_order,
    )
    return await BannerService.update_banner(banner_id, request, image)


@router.patch(
    "/{banner_id}/toggle",
    response_model=BannerResponse,
    description="배너의 활성화 상태를 토글합니다. (활성화↔비활성화)",
)
async def toggle_banner_status(banner_id: int = Path(..., description="토글할 배너의 ID")) -> BannerResponse:
    """
    배너 활성화 상태 토글

    - 활성화된 배너는 비활성화로 변경
    - 비활성화된 배너는 활성화로 변경
    """
    return await BannerService.toggle_banner_status(banner_id)


@router.delete("/{banner_id}", status_code=204, description="배너를 삭제합니다. 이미지 파일도 함께 삭제됩니다.")
async def delete_banner(banner_id: int = Path(..., description="삭제할 배너의 ID")) -> None:
    """
    배너 삭제

    - 배너 정보 삭제
    - 연관된 이미지 파일 삭제
    - 같은 카테고리의 배너 순서 자동 조정
    """
    await BannerService.delete_banner(banner_id)
    return None
