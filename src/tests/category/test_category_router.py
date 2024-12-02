from httpx import AsyncClient
from starlette.testclient import TestClient
from tortoise.contrib.test import TestCase

from app.category.models.category import Category
from main import app


class TestCategoryRouter(TestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.test_category = await Category.create(
            name="Test Category",
            depth=0,
        )
        self.sub_category = await Category.create(
            name="Sub Category",
            parent_id=self.test_category.id,
            depth=1,
        )

    async def test_categories(self) -> None:
        # Given
        category = await Category.get(name="Test Category")
        assert category.name == "Test Category"

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url="/api/v1/category",  # Update the URL if necessary
                headers={"Accept": "application/json"},
            )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["name"] == "Test Category"
