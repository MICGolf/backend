from httpx import AsyncClient
from tortoise.contrib.test import TestCase

from app.category.models.category import Category


class TestArticleRouter(TestCase):
    async def test_get_article_and_comment(self) -> None:
        # given
        name = "test_category_id"
        category = await Category.create(name=name, depth=1)

        # # when
        # async with AsyncClient(app=app, base_url="http://test") as ac:
        #     response = await ac.get(
        #         url=f"/v1/articles/{article_id}",
        #         headers={"Accept": "application/json"},
        #     )
        #
        # # then
        # self.assertEqual(response.status_code, 200)
        # response_body = response.json()
        # self.assertEqual(response_body["id"], article_id)
        # self.assertEqual(response_body["author"], "author")
        # self.assertEqual(response_body["title"], "title")
        # self.assertEqual(response_body["body"], "body")
        #
        # self.assertEqual(len(response_body["comments"]), 2)
        # self.assertEqual(response_body["comments"][0]["id"], "comment1")
        # self.assertEqual(response_body["comments"][0]["author"], "c1_author")
        # self.assertEqual(response_body["comments"][0]["body"], "c1_body")
        #
        # self.assertEqual(response_body["comments"][1]["id"], "comment2")
        # self.assertEqual(response_body["comments"][1]["author"], "c2_author")
        # self.assertEqual(response_body["comments"][1]["body"], "c2_body")
