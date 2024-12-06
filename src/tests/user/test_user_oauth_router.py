from unittest.mock import AsyncMock, patch

import httpx
from httpx import AsyncClient
from tortoise.contrib.test import TestCase

from app.user.dtos.request import UserCreateRequestDTO
from app.user.models.user import User
from app.user.services.auth_service import AuthenticateService
from app.user.services.user_service import UserService
from common.utils.email_services import get_email_service
from common.utils.sms_services import get_sms_service
from main import app


class TestUserService(TestCase):

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        auth_service = AuthenticateService()
        sms_service = get_sms_service()
        email_service = get_email_service()

        self.user_service = UserService(
            auth_service=auth_service,
            sms_service=sms_service,
            email_service=email_service,
        )
        self.user_kakao = await self.user_service.create_social_user(
            name="홍길동",
            email="test_kakao@naver.com",
            social_id="kkkkk",
            social_login_type="kakao",
        )
        self.user_naver = await self.user_service.create_social_user(
            name="홍길동",
            email="test_naver@naver.com",
            social_id="nnnnn",
            social_login_type="naver",
        )

    @patch("app.user.services.auth_service.AuthenticateService._get_kakao_access_token")
    @patch("app.user.services.auth_service.AuthenticateService._get_kakao_user_info")
    async def test_social_회원가입_및_로그인_카카오_신규유저(
        self,
        mock_get_kakao_user_info: AsyncMock,
        mock_get_kakao_access_token: AsyncMock,
    ) -> None:
        # Given

        mock_get_kakao_access_token.return_value = "fake_access_token"
        mock_get_kakao_user_info.return_value = {
            "id": "12345",
            "kakao_account": {"email": "test@example.com"},
            "properties": {"nickname": "Test User"},
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/kakao",
                headers={
                    "Accept": "application/json",
                    "code": "fake_code",
                },
            )

        # Then
        user = await User.filter(email="test@example.com").first()

        if user is None:
            self.fail("User not found")

        assert response.status_code == 200
        assert response.json()["access_token"] is not None
        assert user.social_id == "12345"
        assert user.social_login_type == "kakao"

    @patch("app.user.services.auth_service.AuthenticateService._get_kakao_access_token")
    @patch("app.user.services.auth_service.AuthenticateService._get_kakao_user_info")
    async def test_social_회원가입_및_로그인_카카오_기존유저(
        self,
        mock_get_kakao_user_info: AsyncMock,
        mock_get_kakao_access_token: AsyncMock,
    ) -> None:
        # Given
        mock_get_kakao_access_token.return_value = "fake_access_token"
        mock_get_kakao_user_info.return_value = {
            "id": "kkkkk",
            "kakao_account": {"email": "test_kakao@naver.com"},
            "properties": {"nickname": "홍길동"},
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/kakao",
                headers={
                    "Accept": "application/json",
                    "code": "fake_code",
                },
            )

        # Then
        user = await User.filter(email=self.user_kakao.email).first()

        if user is None:
            self.fail("User not found")

        assert response.status_code == 200
        assert response.json()["access_token"] is not None
        assert user.social_id == "kkkkk"
        assert user.social_login_type == "kakao"

    @patch("app.user.services.auth_service.AuthenticateService._get_naver_access_token")
    @patch("app.user.services.auth_service.AuthenticateService._get_naver_user_info")
    async def test_social_회원가입_및_로그인_네이버_신규유저(
        self,
        mock_get_kakao_user_info: AsyncMock,
        mock_get_kakao_access_token: AsyncMock,
    ) -> None:
        # Given
        mock_get_kakao_access_token.return_value = "fake_access_token"
        mock_get_kakao_user_info.return_value = {
            "response": {
                "id": "1234567",
                "email": "test@example.com",
                "name": "Test User",
            }
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/naver",
                headers={
                    "Accept": "application/json",
                    "code": "fake_code",
                },
            )

        # Then
        user = await User.filter(email="test@example.com").first()

        if user is None:
            self.fail("User not found")

        assert response.status_code == 200
        assert response.json()["access_token"] is not None
        assert user.social_id == "1234567"
        assert user.social_login_type == "naver"

    @patch("app.user.services.auth_service.AuthenticateService._get_naver_access_token")
    @patch("app.user.services.auth_service.AuthenticateService._get_naver_user_info")
    async def test_social_회원가입_및_로그인_네이버_기존유저(
        self,
        mock_get_kakao_user_info: AsyncMock,
        mock_get_kakao_access_token: AsyncMock,
    ) -> None:
        # Given
        mock_get_kakao_access_token.return_value = "fake_access_token"
        mock_get_kakao_user_info.return_value = {
            "response": {
                "id": "nnnnn",
                "email": "test_naver@naver.com",
                "name": "홍길동",
            }
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/naver",
                headers={
                    "Accept": "application/json",
                    "code": "fake_code",
                },
            )

        # Then
        user = await User.filter(email=self.user_naver.email).first()

        if user is None:
            self.fail("User not found")

        assert response.status_code == 200
        assert response.json()["access_token"] is not None
        assert user.social_id == "nnnnn"
        assert user.social_login_type == "naver"

    @patch("app.user.services.auth_service.AuthenticateService._request_token")
    async def test_social_카카오_요청_실패(self, mock_request_token: AsyncMock) -> None:
        # Given
        mock_request_token.return_value = httpx.Response(status_code=400)

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/kakao",
                headers={
                    "Accept": "application/json",
                },
            )

        # Then
        assert response.status_code == 500
        assert response.json()["code"] == 2003

    @patch("app.user.services.auth_service.AuthenticateService._request_token")
    async def test_social_네이버_요청_실패(self, mock_request_token: AsyncMock) -> None:
        # Given
        mock_request_token.return_value = httpx.Response(status_code=400)

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/naver",
                headers={
                    "Accept": "application/json",
                },
            )

        # Then
        assert response.status_code == 500
        assert response.json()["code"] == 2005

    @patch("app.user.services.auth_service.AuthenticateService._request_token")
    @patch("app.user.services.auth_service.AuthenticateService._is_valid_token_format")
    async def test_social_카카오_토큰_유효성_실패(
        self, mock_is_valid_token_format: AsyncMock, mock_request_token: AsyncMock
    ) -> None:
        # Given
        mock_is_valid_token_format.return_value = False
        mock_request_token.return_value = httpx.Response(status_code=200, json={"access_token": "asd"})

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/kakao",
                headers={
                    "Accept": "application/json",
                },
            )

        # Then
        assert response.status_code == 400
        assert response.json()["code"] == 2004

    @patch("app.user.services.auth_service.AuthenticateService._request_token")
    @patch("app.user.services.auth_service.AuthenticateService._is_valid_token_format")
    async def test_social_네이버_토큰_유효성_실패(
        self, mock_is_valid_token_format: AsyncMock, mock_request_token: AsyncMock
    ) -> None:
        # Given
        mock_is_valid_token_format.return_value = False
        mock_request_token.return_value = httpx.Response(status_code=200, json={"access_token": "asd"})

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/naver",
                headers={
                    "Accept": "application/json",
                },
            )

        # Then
        assert response.status_code == 400
        assert response.json()["code"] == 2006

    async def test_지원하지_않는_social_타입(self) -> None:
        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/google",
                headers={
                    "Accept": "application/json",
                },
            )

        # Then
        assert response.status_code == 400
        assert response.json()["code"] == 2002

    @patch("app.user.services.auth_service.AuthenticateService._get_kakao_access_token")
    @patch("app.user.services.auth_service.AuthenticateService._get_kakao_user_info")
    async def test_기존회원_소셜로그인_연동(
        self,
        mock_get_kakao_user_info: AsyncMock,
        mock_get_kakao_access_token: AsyncMock,
    ) -> None:
        # Given
        user_data = {
            "name": "홍길동2",
            "email": "hong2@example.com",
            "phone": "010-1235-1234",
            "login_id": "hong2",
            "password": "Password1!",
            "password2": "Password1!",
        }

        body = UserCreateRequestDTO(**user_data)

        normal_user = await self.user_service.create_user(body)

        mock_get_kakao_access_token.return_value = "fake_access_token"
        mock_get_kakao_user_info.return_value = {
            "id": "hhhhh",
            "kakao_account": {"email": "hong2@example.com"},
            "properties": {"nickname": "홍길동2"},
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/kakao",
                headers={
                    "Accept": "application/json",
                    "code": "fake_code",
                },
            )

        # Then
        user = await User.filter(email=normal_user.email).first()

        if user is None:
            self.fail("User not found")

        assert response.status_code == 200
        assert response.json()["access_token"] is not None
        assert user.email == normal_user.email
        assert user.social_id == "hhhhh"
        assert user.social_login_type == "kakao"

    @patch("app.user.services.auth_service.AuthenticateService._get_kakao_access_token")
    @patch("app.user.services.auth_service.AuthenticateService._get_kakao_user_info")
    async def test_카카오_네이버_이메일_충돌(
        self,
        mock_get_kakao_user_info: AsyncMock,
        mock_get_kakao_access_token: AsyncMock,
    ) -> None:

        mock_get_kakao_access_token.return_value = "fake_access_token"
        mock_get_kakao_user_info.return_value = {
            "id": "nnnnn",
            "kakao_account": {"email": "test_naver@naver.com"},
            "properties": {"nickname": "홍길동"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/oauth/kakao",
                headers={
                    "Accept": "application/json",
                    "code": "fake_code",
                },
            )

        assert response.status_code == 409
        assert response.json()["code"] == 2001
