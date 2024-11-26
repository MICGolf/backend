from tortoise.contrib.test import TestCase

from app.banner.models.banner import Banner, BannerType
from app.banner.services.banner_service import BannerService
from common.utils.pagination_and_sorting_dto import PaginationAndSortingDTO


class TestBannerService(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
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
        # When
        response = await BannerService.get_banners()

        # Then
        assert len(response.items) == 1
        assert response.items[0].title == "Test Banner"

    async def test_get_banners_with_pagination(self) -> None:
        # Given
        pagination = PaginationAndSortingDTO(page=1, page_size=10, sort="created_at", order="desc")

        # When
        response = await BannerService.get_banners(pagination=pagination)

        # Then
        assert response.page == 1
        assert response.page_size == 10
        assert len(response.items) == 1

    async def test_get_banners_by_type(self) -> None:
        # When
        response = await BannerService.get_banners(query_type=BannerType.BANNER)

        # Then
        assert len(response.items) == 1
        assert response.items[0].category_type == BannerType.BANNER

    async def test_toggle_banner_status(self) -> None:
        # Given
        banner = await Banner.get_or_none(id=self.banner.pk)
        assert banner is not None
        original_status = banner.is_active

        # When
        response = await BannerService.toggle_banner_status(banner.pk)

        # Then
        assert response.is_active != original_status

    async def test_delete_banner(self) -> None:
        # Given
        banner = await Banner.get_or_none(id=self.banner.pk)
        assert banner is not None

        # When
        result = await BannerService.delete_banner(banner.pk)

        # Then
        assert result is True
        deleted_banner = await Banner.get_or_none(id=banner.pk)
        assert deleted_banner is None
