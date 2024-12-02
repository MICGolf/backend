# tests/category/test_services.py
from fastapi import HTTPException
from tortoise.contrib.test import TestCase

from app.category.dtos.category_request import CategoryCreateRequest, CategoryUpdateRequest
from app.category.models.category import Category
from app.category.services.category_services import CategoryService


class TestCategoryService(TestCase):
    async def test_get_categories(self) -> None:
        # given
        await Category.create(name="Category 1")
        await Category.create(name="Category 2")

        # when
        categories = await CategoryService.get_categories(page=1, limit=10)

        # then
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].name, "Category 1")
        self.assertEqual(categories[1].name, "Category 2")

    async def test_get_category_detail_success(self) -> None:
        # given
        category = await Category.create(name="Test Category")

        # when
        response = await CategoryService.get_category_detail(category.pk)

        # then
        self.assertEqual(response.id, category.pk)
        self.assertEqual(response.name, category.name)

    async def test_get_category_detail_not_found(self) -> None:
        # when & then
        with self.assertRaises(HTTPException) as context:
            await CategoryService.get_category_detail(999)
        self.assertEqual(context.exception.status_code, 404)

    async def test_create_category_success(self) -> None:
        # given
        request = CategoryCreateRequest(name="New Category")

        # when
        response = await CategoryService.create_category(request)

        # then
        self.assertEqual(response.name, "New Category")
        self.assertEqual(response.depth, 0)
        self.assertIsNone(response.parent_id)

    async def test_create_subcategory_success(self) -> None:
        # given
        parent = await Category.create(name="Parent")
        request = CategoryCreateRequest(name="Child", parent_id=parent.pk)

        # when
        response = await CategoryService.create_category(request)

        # then
        self.assertEqual(response.name, "Child")
        self.assertEqual(response.parent_id, parent.pk)
        self.assertEqual(response.depth, 1)

    async def test_create_category_parent_not_found(self) -> None:
        # given
        request = CategoryCreateRequest(name="Test", parent_id=999)

        # when & then
        with self.assertRaises(HTTPException) as context:
            await CategoryService.create_category(request)
        self.assertEqual(context.exception.status_code, 404)

    async def test_update_category_success(self) -> None:
        # given
        category = await Category.create(name="Old Name")
        request = CategoryUpdateRequest(name="New Name")

        # when
        response = await CategoryService.update_category(category.pk, request)

        # then
        self.assertEqual(response.name, "New Name")

    async def test_delete_category_success(self) -> None:
        # Given: 최상위 카테고리가 아닌 하위 카테고리 생성
        parent = await Category.create(name="Parent Category", depth=0)
        child_category = await Category.create(
            name="Child To Delete", parent_id=parent.pk, depth=1  # 하위 카테고리여야 함
        )

        # When
        await CategoryService.delete_category(child_category.pk)

        # Then
        deleted = await Category.get_or_none(id=child_category.pk)
        self.assertIsNone(deleted)

    async def test_delete_category_with_subcategories(self) -> None:
        # given
        parent = await Category.create(name="Parent")
        child = await Category.create(name="Child", parent_id=parent.pk, depth=1)

        # when
        await CategoryService.delete_category(parent.pk)

        # then
        # 부모와 자식 카테고리 모두 삭제되었는지 확인
        deleted_parent = await Category.get_or_none(id=parent.pk)
        deleted_child = await Category.get_or_none(id=child.pk)
        self.assertIsNone(deleted_parent)
        self.assertIsNone(deleted_child)
