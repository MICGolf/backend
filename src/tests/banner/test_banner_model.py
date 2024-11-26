from tortoise.contrib.test import TestCase

from app.banner.models.banner import Banner, BannerType


class TestBannerModels(TestCase):
    async def test_banner_crud(self) -> None:
        # Create
        banner = await Banner.create(
            title="Test Banner",
            sub_title="Test Sub Title",
            image_url="http://example.com/test.jpg",
            event_url="http://example.com/event",
            is_active=True,
            category_type=BannerType.BANNER,
            display_order=1,
        )

        # Read
        saved_banner = await Banner.get_or_none(pk=banner.pk)
        assert saved_banner is not None
        assert saved_banner.title == "Test Banner"

        # Update
        await banner.update_from_dict({"title": "Updated Banner"}).save()
        updated_banner = await Banner.get_or_none(pk=banner.pk)
        assert updated_banner is not None
        assert updated_banner.title == "Updated Banner"

        # Delete
        await banner.delete()
        deleted_banner = await Banner.get_or_none(pk=banner.pk)
        assert deleted_banner is None

    async def test_get_by_type(self) -> None:
        # Given
        await Banner.create(
            title="Test Banner",
            sub_title="Test Sub Title",
            image_url="http://example.com/test.jpg",
            event_url="http://example.com/event",
            is_active=True,
            category_type=BannerType.BANNER,
            display_order=1,
        )

        # When
        banners = await Banner.get_by_type(BannerType.BANNER)

        # Then
        assert len(banners) == 1
        assert banners[0].title == "Test Banner"
