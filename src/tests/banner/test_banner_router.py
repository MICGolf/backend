from io import BytesIO

from fastapi import FastAPI
from httpx import AsyncClient
from PIL import Image
from tortoise.contrib.test import TestCase

from app.banner.models.banner import Banner, BannerType
from app.banner.router import router as banner_router


class TestBannerRouter(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        # FastAPI 앱 설정
        self.app = FastAPI()
        self.app.include_router(banner_router, prefix="/api/v1")

        # 테스트용 배너 생성
        self.banner = await Banner.create(
            title="Test Banner",
            sub_title="Test Sub Title",
            image_url="http://example.com/banner.jpg",
            event_url="http://example.com/event",
            is_active=True,
            category_type=BannerType.BANNER,
            display_order=1,
        )

    async def test_get_banners(self) -> None:
        async with AsyncClient(app=self.app, base_url="http://test", follow_redirects=True) as ac:
            response = await ac.get("/api/v1/banners")
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert len(data["items"]) > 0

    async def test_get_banners_with_query(self) -> None:
        async with AsyncClient(app=self.app, base_url="http://test", follow_redirects=True) as ac:
            response = await ac.get("/api/v1/banners?query=banner")
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            for item in data["items"]:
                assert item["banner_type"] == "banner"

    async def test_toggle_banner_status(self) -> None:
        async with AsyncClient(app=self.app, base_url="http://test", follow_redirects=True) as ac:
            response = await ac.patch(f"/api/v1/banners/{self.banner.pk}/toggle")
            assert response.status_code == 200
            data = response.json()
            assert data["is_active"] != self.banner.is_active
