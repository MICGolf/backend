import os
from datetime import datetime
from typing import Any, Optional, Tuple

from fastapi import HTTPException, UploadFile
from PIL import Image
from tortoise.expressions import F
from tortoise.transactions import atomic

from app.banner.dtos.request import BannerCreateRequest, BannerUpdateRequest
from app.banner.dtos.response import BannerListResponse, BannerResponse
from app.banner.models.banner import Banner
from common.utils.pagination_and_sorting_dto import PaginationAndSortingDTO
from core.configs import settings


class BannerService:
    """배너 서비스

    배너와 프로모션의 CRUD 및 상태 관리를 담당하는 서비스 클래스입니다.
    이미지 업로드, 순서 관리, 활성화 상태 관리 등의 기능을 제공합니다.

    Attributes:
        ALLOWED_SORT_FIELDS: 허용된 정렬 필드 목록
        IMAGE_SIZE: 요구되는 이미지 크기 (1920x1080 픽셀)
    """

    ALLOWED_SORT_FIELDS = ["created_at", "display_order", "title"]
    IMAGE_SIZE = (1920, 1080)

    @classmethod
    async def get_banners(
        cls, query_type: str | None = None, pagination: PaginationAndSortingDTO | None = None
    ) -> BannerListResponse:
        """배너 목록 조회 (페이지네이션)

        처리 과정:
        1. 카테고리 필터링 (banner/promotion)
        2. 전체 개수 조회
        3. 페이지네이션 적용
        4. 정렬 기준 적용
        5. 결과 반환

        Args:
            query_type: 조회할 배너 타입
            pagination: 페이지네이션 및 정렬 정보

        Returns:
            페이지네이션된 배너 목록
        """
        query = Banner.all()

        if query_type:
            query = query.filter(category_type=query_type)

        total = await query.count()

        # 먼저 현재 카테고리의 모든 배너를 가져와서 순서 재조정
        banners = await query.all()
        category_groups: dict[str, list[Banner]] = {}

        # 카테고리별로 그룹화
        for banner in banners:
            if banner.category_type not in category_groups:
                category_groups[banner.category_type] = []
            category_groups[banner.category_type].append(banner)

        # 각 카테고리별로 순서 재조정
        for category_type, category_banners in category_groups.items():
            # 생성일시 순으로 정렬
            sorted_banners = sorted(category_banners, key=lambda x: x.created_at)

            # 순서 재할당
            for index, banner in enumerate(sorted_banners, start=1):
                if banner.display_order != index:
                    await banner.update_from_dict({"display_order": index}).save()

        # 정렬된 쿼리 실행
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

        # 최종 결과 조회
        result_banners = await query

        return BannerListResponse(
            items=[BannerResponse.from_banner(banner) for banner in result_banners],
            total=total,
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else len(result_banners),
        )

    @classmethod
    async def _validate_and_adjust_display_order(cls, category_type: str, desired_order: int | None = None) -> int:
        """배너 순서 검증 및 조정

        같은 카테고리 내에서 배너의 순서를 검증하고 조정합니다.

        처리 과정:
        1. 현재 카테고리의 모든 배너 조회
        2. 원하는 순서가 없으면 마지막 순서 + 1 반환
        3. 순서 범위 검증 (1 이상)
        4. 기존 배너들의 순서 재조정

        Args:
            category_type: 배너 타입 (banner/promotion)
            desired_order: 원하는 순서 (None인 경우 마지막 순서 + 1)

        Returns:
            최종 display_order 값
        """
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
    async def _process_image(image: UploadFile, old_image_path: str | None = None) -> Tuple[str, str]:
        """이미지 처리 및 저장

        처리 과정:
        1. 기존 이미지 삭제 (있는 경우)
        2. 새 파일명 생성 (타임스탬프 포함)
        3. 이미지 최적화 (RGB 변환, JPEG 압축)
        4. 파일 저장

        Args:
            image: 업로드된 이미지 파일
            old_image_path: 기존 이미지 경로

        Returns:
            Tuple[저장된 파일 경로, 파일명]

        Raises:
            HTTPException: 이미지 처리 실패 시 (400)
        """
        try:
            if old_image_path and os.path.exists(old_image_path):
                os.remove(old_image_path)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{image.filename}"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            content = await image.read()
            with Image.open(image.file) as img:
                img = img.convert("RGB")
                img.save(file_path, "JPEG", quality=85, optimize=True)

            return file_path, filename
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"이미지 처리 실패: {str(e)}")

    @staticmethod
    def _validate_image(image: Optional[UploadFile]) -> None:
        """이미지 유효성 검증

        검증 항목:
        1. 파일 존재 여부
        2. 이미지 파일 형식 확인
        3. JPG 확장자 확인

        Args:
            image: 검증할 이미지 파일

        Raises:
            HTTPException:
                - 이미지 파일이 없는 경우 (400)
                - 이미지 형식이 아닌 경우 (400)
                - JPG 형식이 아닌 경우 (400)
        """
        if not image:
            raise HTTPException(status_code=400, detail="이미지 파일이 필요합니다")

        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다")

        if not image.filename or not image.filename.lower().endswith(".jpg"):
            raise HTTPException(status_code=400, detail="JPG 형식의 이미지만 업로드 가능합니다")

    @classmethod
    @atomic()
    async def create_banner(
        cls,
        request: BannerCreateRequest,
        image: UploadFile,
    ) -> BannerResponse:
        """배너 생성

        처리 과정:
        1. 이미지 유효성 검증
        2. 이미지 저장 및 최적화
        3. 배너 순서 자동 설정
        4. 배너 정보 저장

        Args:
            request: 배너 생성 정보
            image: 배너 이미지 파일

        Returns:
            생성된 배너 정보

        Raises:
            HTTPException: 이미지 관련 오류 시 (400)
        """
        cls._validate_image(image)

        file_path, _ = await cls._process_image(image)
        display_order = await cls._validate_and_adjust_display_order(request.banner_type)

        banner = await Banner.create(
            title=request.title,
            sub_title=request.subTitle,
            event_url=request.eventUrl,
            image_url=file_path,
            category_type=request.banner_type,
            is_active=request.is_active,
            display_order=display_order,
        )

        return BannerResponse.from_banner(banner)

    @classmethod
    @atomic()
    async def update_banner(
        cls, banner_id: int, request: BannerUpdateRequest, image: Optional[UploadFile] = None
    ) -> BannerResponse:
        """배너 수정

        처리 과정:
        1. 배너 존재 확인
        2. 카테고리/순서 변경 시 순서 재조정
        3. 이미지 변경 시 기존 이미지 삭제 및 새 이미지 저장
        4. 배너 정보 업데이트

        Args:
            banner_id: 수정할 배너 ID
            request: 수정할 배너 정보
            image: 새로운 이미지 파일 (선택사항)

        Returns:
            수정된 배너 정보

        Raises:
            HTTPException:
                - 배너가 존재하지 않는 경우 (404)
                - 이미지 관련 오류 시 (400)
        """
        banner = await Banner.get_or_none(id=banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="배너를 찾을 수 없습니다")

        update_data: dict[str, Any] = request.model_dump(exclude_unset=True)

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

        if image:
            cls._validate_image(image)
            file_path, _ = await cls._process_image(image, banner.image_url)
            update_data["image_url"] = file_path

        await banner.update_from_dict(update_data).save()
        return BannerResponse.from_banner(banner)

    @classmethod
    @atomic()
    async def toggle_banner_status(cls, banner_id: int) -> BannerResponse:
        """배너 활성화 상태 토글

        배너의 활성화 상태를 반전시킵니다. (활성화 ↔ 비활성화)

        Args:
            banner_id: 토글할 배너 ID

        Returns:
            토글된 배너 정보

        Raises:
            HTTPException: 배너가 존재하지 않는 경우 (404)
        """
        banner = await Banner.get_or_none(id=banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="배너를 찾을 수 없습니다")

        banner.is_active = not banner.is_active
        await banner.save()
        return BannerResponse.from_banner(banner)

    @classmethod
    @atomic()
    async def delete_banner(cls, banner_id: int) -> bool:
        """배너 삭제

        처리 과정:
        1. 배너 존재 확인
        2. 연관된 이미지 파일 삭제
        3. 같은 카테고리의 배너 순서 재조정
        4. 배너 정보 삭제

        Args:
            banner_id: 삭제할 배너 ID

        Returns:
            삭제 성공 여부

        Raises:
            HTTPException: 배너가 존재하지 않는 경우 (404)
        """
        banner = await Banner.get_or_none(id=banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="배너를 찾을 수 없습니다")

        if banner.image_url and os.path.exists(banner.image_url):
            try:
                os.remove(banner.image_url)
            except OSError:
                pass

        await Banner.filter(category_type=banner.category_type, display_order__gt=banner.display_order).update(
            display_order=F("display_order") - 1
        )

        await banner.delete()
        return True
