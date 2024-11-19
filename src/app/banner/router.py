from fastapi import APIRouter, File, Form, UploadFile, Query
from typing import List
from app.banner.services.banner_service import BannerService
from app.banner.dtos.request import BannerCreateRequest, BannerUpdateRequest
from app.banner.dtos.response import BannerResponse
from core.configs import settings

router = APIRouter(prefix="/banners", tags=["배너"])


@router.get("/", response_model=List[BannerResponse])
async def get_banners(
    query: str | None = Query(
        None,
        description="조회할 타입 (banner/promotion)",
        regex="^(banner|promotion)$"
    )
):
    """배너 목록 조회"""
    return await BannerService.get_banners(query_type=query)


@router.post("/", response_model=BannerResponse)
async def create_banner(
    title: str = Form(...),
    redirect_url: str | None = Form(None),
    banner_type: str = Form(...),
    is_active: bool = Form(True),
    image: UploadFile = File(...)
):
    """배너 생성"""
    request = BannerCreateRequest(
        title=title,
        redirect_url=redirect_url,
        banner_type=banner_type,
        is_active=is_active
    )
    return await BannerService.create_banner(request, image, upload_dir=settings.UPLOAD_DIR)


@router.patch("/{banner_id}", response_model=BannerResponse)
async def update_banner(
    banner_id: int,
    title: str | None = Form(None),
    redirect_url: str | None = Form(None),
    is_active: bool | None = Form(None),
    display_order: int | None = Form(None),
    image: UploadFile | None = File(None)
):
    """배너 수정"""
    request = BannerUpdateRequest(
        title=title,
        redirect_url=redirect_url,
        is_active=is_active,
        display_order=display_order
    )
    return await BannerService.update_banner(banner_id, request, image)


@router.patch("/{banner_id}/toggle", response_model=BannerResponse)
async def toggle_banner_status(banner_id: int):
    """배너 활성화 상태 토글"""
    return await BannerService.toggle_banner_status(banner_id)


@router.delete("/{banner_id}", status_code=204)
async def delete_banner(banner_id: int):
    """배너 삭제"""
    await BannerService.delete_banner(banner_id)
    return None