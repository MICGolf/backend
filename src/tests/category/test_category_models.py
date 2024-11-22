# tests/category/test_models.py
from tortoise.contrib.test import TestCase

from app.category.models.category import Category


class TestCategoryModel(TestCase):
    async def test_create_category(self) -> None:
        # given & when
        category = await Category.create(name="Test Category")

        # then
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.depth, 0)
        self.assertIsNone(category.parent_id)  # type: ignore

    async def test_create_subcategory(self) -> None:
        # given
        parent = await Category.create(name="Parent Category")

        # when
        child = await Category.create(name="Child Category", parent_id=parent.pk, depth=1)

        # then
        self.assertEqual(child.name, "Child Category")
        self.assertEqual(child.parent_id, parent.pk)  # type: ignore
        self.assertEqual(child.depth, 1)

    async def test_update_category(self) -> None:
        # given
        category = await Category.create(name="Old Name")

        # when
        await category.update_from_dict({"name": "New Name"}).save()
        updated_category = await Category.get(id=category.pk)

        # then
        self.assertEqual(updated_category.name, "New Name")

    async def test_delete_category(self) -> None:
        # given
        category = await Category.create(name="To Delete")

        # when
        await category.delete()
        deleted_category = await Category.get_or_none(id=category.pk)

        # then
        self.assertIsNone(deleted_category)
