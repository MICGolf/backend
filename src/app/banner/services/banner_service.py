import os
from fastapi import HTTPException, UploadFile
from tortoise.expressions import F
from app.banner.models.banner import Banner
from app.banner.dtos.request import BannerCreateRequest, BannerUpdateRequest
from app.banner.dtos.response import BannerResponse


class BannerService:
    @staticmethod
    async def get_banners(query_type: str | None = None) -> list[BannerResponse]:
        """배너 목록 조회"""
        banners = await Banner.get_by_type(query_type)
        return [BannerResponse.from_banner(banner) for banner in banners]

    @staticmethod
    async def create_banner(
            request: BannerCreateRequest,
            image: UploadFile,
            upload_dir: str = "uploads/banners"
    ) -> BannerResponse:
        """배너 생성"""
        import os
        from datetime import datetime

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as f:
            content = await image.read()
            f.write(content)

        last_banner = await Banner.filter(banner_type=request.banner_type).order_by("-display_order").first()
        display_order = (last_banner.display_order + 1) if last_banner else 0

        banner = await Banner.create(
            **request.model_dump(),
            image_url=file_path,
            display_order=display_order
        )

        return BannerResponse.from_banner(banner)

    @staticmethod
    async def update_banner(
            banner_id: int,
            request: BannerUpdateRequest,
            image: UploadFile | None = None
    ) -> BannerResponse:
        """배너 수정"""
        banner = await Banner.get_or_none(id=banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="Banner not found")

        update_data = request.model_dump(exclude_unset=True)

        if image:
            import os
            from datetime import datetime

            # 기존 이미지 삭제
            if banner.image_url and os.path.exists(banner.image_url):
                os.remove(banner.image_url)

            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}"
            file_path = os.path.join("uploads/banners", filename)

            with open(file_path, "wb") as f:
                content = await image.read()
                f.write(content)

            update_data["image_url"] = file_path

        await banner.update_from_dict(update_data).save()
        return BannerResponse.from_banner(banner)

    @staticmethod
    async def toggle_banner_status(banner_id: int) -> BannerResponse:
        """배너 활성화 상태 토글"""
        banner = await Banner.get_or_none(id=banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="Banner not found")

        banner.is_active = not banner.is_active
        await banner.save()
        return BannerResponse.from_banner(banner)

    @staticmethod
    async def delete_banner(banner_id: int) -> bool:
        """배너 삭제"""
        banner = await Banner.get_or_none(id=banner_id)
        if not banner:
            raise HTTPException(status_code=404, detail="Banner not found")

        # 이미지 파일 삭제
        if banner.image_url and os.path.exists(banner.image_url):
            try:
                os.remove(banner.image_url)
            except OSError:
                pass  # 이미지 삭제 실패해도 배너는 삭제 진행

        # 같은 타입의 다른 배너들의 순서 재조정
        await Banner.filter(
            banner_type=banner.banner_type,
            display_order__gt=banner.display_order
        ).update(display_order=F('display_order') - 1)

        await banner.delete()
        return True