from fastapi import FastAPI
from httpx import AsyncClient
from tortoise.contrib.test import TestCase

from app.category.models.category import Category
from app.category.router import router as category_router  # 추가
from main import app


class TestCategoryRouter(TestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()  # ORM 초기화

        self.app = FastAPI()
        self.app.include_router(category_router)  # 카테고리 라우터 등록

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
        # Given: Ensure the test_category is available
        category = await Category.get(name="Test Category")
        assert category.name == "Test Category"

        # When: Make the GET request
        async with AsyncClient(app=self.app, base_url="http://test") as ac:
            response = await ac.get(
                url="/category",
                headers={"Accept": "application/json"},
            )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["name"] == "Test Category"
