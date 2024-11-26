from datetime import datetime
from io import BytesIO
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from PIL import Image
from tortoise.expressions import F
from tortoise.transactions import atomic

from app.banner.dtos.request import BannerCreateRequest, BannerUpdateRequest
from app.banner.dtos.response import BannerListResponse, BannerResponse
from app.banner.models.banner import Banner
from common.utils.ncp_s3_client import get_object_storage_client
from common.utils.pagination_and_sorting_dto import PaginationAndSortingDTO
from core.configs import settings


class BannerService:
    """배너 서비스 클래스"""

    ALLOWED_SORT_FIELDS = ["created_at", "display_order", "title"]
    IMAGE_SIZE = (1920, 1080)

    @classmethod
    async def get_banners(
        cls, query_type: str | None = None, pagination: PaginationAndSortingDTO | None = None
    ) -> BannerListResponse:
        """배너 목록을 조회하고 페이지네이션 처리"""
        query = Banner.all()
        if query_type:
            query = query.filter(category_type=query_type)

        total = await query.count()
        banners = await query.all()

        category_groups: dict[str, list[Banner]] = {}
        for banner in banners:
            if banner.category_type not in category_groups:
                category_groups[banner.category_type] = []
            category_groups[banner.category_type].append(banner)

        for category_type, category_banners in category_groups.items():
            sorted_banners = sorted(category_banners, key=lambda x: x.created_at)
            for index, banner in enumerate(sorted_banners, start=1):
                if banner.display_order != index:
                    await banner.update_from_dict({"display_order": index}).save()

        if pagination:
            if pagination.sort not in cls.ALLOWED_SORT_FIELDS:
                raise HTTPException(status_code=400, detail=f"정렬은 {', '.join(cls.ALLOWED_SORT_FIELDS)}만 가능합니다")

            order_prefix = "-" if pagination.order == "desc" else ""
            sort_field = f"{order_prefix}{pagination.sort}"
            query = query.order_by("category_type", "display_order", sort_field)

            skip = (pagination.page - 1) * pagination.page_size
            query = query.offset(skip).limit(pagination.page_size)
        else:
            query = query.order_by("category_type", "display_order", "-created_at")

        result_banners = await query

        return BannerListResponse(
            items=[BannerResponse.from_banner(banner) for banner in result_banners],
            total=total,
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else len(result_banners),
        )

    @classmethod
    async def _validate_and_adjust_display_order(cls, category_type: str, desired_order: int | None = None) -> int:
        """배너 표시 순서를 검증하고 조정"""
        banners = await Banner.filter(category_type=category_type).order_by("display_order").all()
        if not banners:
            return 1

        if desired_order is None:
            return banners[-1].display_order + 1

        current_orders = [banner.display_order for banner in banners]
        max_order = len(current_orders)

        if desired_order < 1:
            desired_order = 1
        elif desired_order > max_order + 1:
            desired_order = max_order + 1

        if desired_order <= max_order:
            await Banner.filter(category_type=category_type, display_order__gte=desired_order).update(
                display_order=F("display_order") + 1
            )

        return desired_order

    @staticmethod
    async def _process_image(image: UploadFile, old_image_url: str | None = None) -> tuple[str, str]:
        try:
            if old_image_url:
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                old_key = old_image_url.split("/")[-1]
                s3_client = get_object_storage_client()
                await s3_client.delete_file(bucket_name, old_key)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid4())[:8]
            filename = f"banner_{timestamp}_{unique_id}.jpg"

            with Image.open(image.file) as img:
                img = img.convert("RGB")
                buffer = BytesIO()
                img.save(buffer, "JPEG", quality=85, optimize=True)
                buffer.seek(0)

            s3_client = get_object_storage_client()
            uploaded_url = await s3_client.upload_file_obj(
                bucket_name=settings.AWS_STORAGE_BUCKET_NAME, file_obj=buffer, object_name=f"banners/{filename}"
            )

            if not uploaded_url:
                raise HTTPException(status_code=500, detail="이미지 업로드 실패")

            return uploaded_url, filename

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"이미지 처리 실패: {str(e)}")

    @staticmethod
    def _validate_image(image: Optional[UploadFile]) -> None:
        """업로드된 이미지의 유효성을 검사"""
        if not image:
            raise HTTPException(status_code=400, detail="이미지 파일이 필요합니다")
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다")
        if not image.filename or not image.filename.lower().endswith((".jpg", ".jpeg")):
            raise HTTPException(status_code=400, detail="JPG 형식의 이미지만 업로드 가능합니다")

    @classmethod
    @atomic()
    async def create_banner(cls, request: BannerCreateRequest, image: UploadFile) -> BannerResponse:
        """새로운 배너를 생성하고 이미지 업로드"""
        cls._validate_image(image)
        image_url, _ = await cls._process_image(image)
        display_order = await cls._validate_and_adjust_display_order(request.category_type)

        banner = await Banner.create(
            title=request.title,
            sub_title=request.sub_title,
            event_url=request.eventUrl,
            image_url=image_url,
            category_type=request.category_type,
            is_active=request.is_active,
            display_order=display_order,
        )

        return BannerResponse.from_banner(banner)

    @classmethod
    @atomic()
    async def update_banner(
        cls, banner_id: int, request: BannerUpdateRequest, image: Optional[UploadFile] = None
    ) -> BannerResponse:
        """기존 배너 정보를 수정하고 이미지 업데이트"""
        banner = await Banner.get_or_none(id=banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="배너를 찾을 수 없습니다")

        update_data: dict[str, Any] = request.model_dump(exclude_unset=True)

        if image:
            cls._validate_image(image)
            image_url, _ = await cls._process_image(image, banner.image_url)
            update_data["image_url"] = image_url

        if (request.category_type and request.category_type != banner.category_type) or (
            request.display_order is not None and request.display_order != banner.display_order
        ):
            await Banner.filter(category_type=banner.category_type, display_order__gt=banner.display_order).update(
                display_order=F("display_order") - 1
            )

            target_category = request.category_type or banner.category_type
            update_data["display_order"] = await cls._validate_and_adjust_display_order(
                target_category, request.display_order
            )

        await banner.update_from_dict(update_data).save()
        return BannerResponse.from_banner(banner)

    @classmethod
    @atomic()
    async def toggle_banner_status(cls, banner_id: int) -> BannerResponse:
        """배너의 활성화 상태를 전환 (활성화↔비활성화)"""
        banner = await Banner.get_or_none(id=banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="배너를 찾을 수 없습니다")

        banner.is_active = not banner.is_active
        await banner.save()
        return BannerResponse.from_banner(banner)

    @classmethod
    @atomic()
    async def delete_banner(cls, banner_id: int) -> bool:
        """배너와 관련 이미지를 삭제하고 순서 재조정"""
        banner = await Banner.get_or_none(id=banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="배너를 찾을 수 없습니다")

        if banner.image_url:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            object_name = banner.image_url.split("/")[-1]
            s3_client = get_object_storage_client()
            await s3_client.delete_file(bucket_name, object_name)

        await Banner.filter(category_type=banner.category_type, display_order__gt=banner.display_order).update(
            display_order=F("display_order") - 1
        )

        await banner.delete()
        return True
