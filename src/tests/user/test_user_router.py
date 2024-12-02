from unittest.mock import patch, AsyncMock

from fastapi import Depends
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
        user_data = {
            "name": "홍길동",
            "email": "hong@example.com",
            "phone": "010-1234-1234",
            "login_id": "hong1",
            "password": "Password1!",
            "password2": "Password1!",
        }

        body = UserCreateRequestDTO(**user_data)

        auth_service = AuthenticateService()
        sms_service = get_sms_service()
        email_service = get_email_service()

        self.user_service = UserService(auth_service=auth_service, sms_service=sms_service, email_service=email_service)

        self.user_1 = await self.user_service.create_user(body)

    async def test_회원가입_id_유효성_검증_성공(self) -> None:
        # Given
        login_id = "test"

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url=f"/api/v1/auth/check-login-id",
                headers={"Accept": "application/json"},
                params={"login_id": login_id},
            )

        # Then
        assert response.status_code == 200

    async def test_회원가입_id_유효성_검증_실패(self) -> None:
        # Given
        login_id = "hong1"

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url=f"/api/v1/auth/check-login-id",
                headers={"Accept": "application/json"},
                params={"login_id": login_id},
            )

        # Then
        assert response.status_code == 400

    async def test_일반_회원가입(self) -> None:
        # Given: Ensure the test_product is available
        user_data = {
            "name": "홍길동2",
            "email": "hong2@example.com",
            "phone": "010-1234-1234",
            "login_id": "hong2",
            "password": "Password1!",
            "password2": "Password1!",
        }
        # When: Make the GET request
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/auth/sign-up",
                headers={"Accept": "application/json"},
                json=user_data,
            )

        assert response.status_code == 201

    async def test_일반_로그인_성공(self) -> None:
        # Given
        login_data = {
            "login_id": "hong1",
            "password": "Password1!",
        }
        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/auth/login",
                headers={"Accept": "application/json"},
                json=login_data,
            )

        assert response.status_code == 200
        assert response.json()["access_token"] is not None

    async def test_일반_로그인_실패_유저_없음(self) -> None:
        # Given
        login_data = {
            "login_id": "없는유저",
            "password": "1234",
        }
        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/auth/login",
                headers={"Accept": "application/json"},
                json=login_data,
            )

        assert response.status_code == 400
        assert response.json()["code"] == 4001

    async def test_일반_로그인_실패_비밀번호_틀림(self) -> None:
        # Given
        login_data = {
            "login_id": "hong1",
            "password": "Passwoㅁㄴㅇ!",
        }
        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/auth/login",
                headers={"Accept": "application/json"},
                json=login_data,
            )

        # Then
        assert response.status_code == 400
        assert response.json()["code"] == 4002

    async def test_사용자_아이디_조회_성공_일반유저(self) -> None:
        # Given
        request_data = {
            "name": "홍길동",
            "email": "hong@example.com",
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url="/api/v1/auth/find-id",
                headers={"Accept": "application/json"},
                params=request_data,
            )

        response_data = response.json()

        # Then
        assert response.status_code == 200
        assert response_data["login_id"] == "hong1"
        assert response_data["login_type"] == "normal"
        assert response_data["social_type"] == "none"

    async def test_사용자_아이디_조회_실패_유저없음(self) -> None:
        # Given
        request_data = {
            "name": "홍길동1",
            "email": "hong@example.com",
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                url="/api/v1/auth/find-id",
                headers={"Accept": "application/json"},
                params=request_data,
            )

        response_data = response.json()

        # Then
        assert response.status_code == 400
        assert response.json()["code"] == 4001

    async def test_사용자_비밀번호_초기화_요청(self) -> None:
        # Given
        request_data = {"login_id": "hong1", "name": "홍길동"}

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/auth/request-password-reset",
                headers={"Accept": "application/json"},
                json=request_data,
            )

        # Then
        assert response.status_code == 200

    async def test_사용자_비밀번호_초기화_성공(self) -> None:
        # Given
        token = await self.user_service.auth_service.generate_reset_token(
            user_id=self.user_1.id, user_name=self.user_1.name
        )

        request_data = {
            "token": token,
            "new_password": "Password123!!",
            "new_password2": "Password123!!",
        }

        old_password = self.user_1.password

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/auth/reset-password",
                headers={"Accept": "application/json"},
                json=request_data,
            )

        # Then
        user = await User.get(id=self.user_1.id)
        new_password = user.password

        assert response.status_code == 200
        assert old_password != new_password

    @patch("app.user.services.auth_service.AuthenticateService.is_valid_reset_token")
    async def test_사용자_비밀번호_초기화_실패_잘못된_토큰(self, mock_is_valid_reset_token: AsyncMock) -> None:
        # Given
        mock_is_valid_reset_token.return_value = False

        token = await self.user_service.auth_service.generate_reset_token(
            user_id=self.user_1.id, user_name=self.user_1.name
        )

        request_data = {
            "token": token,
            "new_password": "Password123!!",
            "new_password2": "Password123!!",
        }

        # When
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                url="/api/v1/auth/reset-password",
                headers={"Accept": "application/json"},
                json=request_data,
            )

        assert response.status_code == 400
        assert response.json()["code"] == 4006
