import random
import time
from typing import Any, cast

import bcrypt
import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBasic, HTTPBearer

from app.user.dtos.auth_dto import JwtPayloadTypedDict, SocialUserInfo
from app.user.dtos.response import JwtTokenResponseDTO
from app.user.models.user import User
from common.constants.auth_constants import (
    JWT_ALGORITHM,
    JWT_EXPIRY_SECONDS,
    JWT_REFRESH_EXPIRY_SECONDS,
    JWT_SECRET_KEY,
    KAKAO_TOKEN_URL,
    KAKAO_USER_INFO_URL,
    NAVER_TOKEN_URL,
    NAVER_USER_INFO_URL,
)
from core.configs import settings

basic_auth = HTTPBasic()


class AuthenticateService:
    @staticmethod
    def hash_password(plain_password: str) -> str:
        plain_password_bytes = plain_password.encode("UTF-8")
        hashed_password = bcrypt.hashpw(plain_password_bytes, bcrypt.gensalt())
        return hashed_password.decode("UTF-8")

    @staticmethod
    def check_password(input_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            input_password.encode("UTF-8"),
            hashed_password.encode("UTF-8"),
        )

    async def get_social_user_info(self, access_token: str, social_type: str) -> SocialUserInfo:
        if social_type == "kakao":
            user_info = await self.get_kakao_user_info(access_token)
            return SocialUserInfo.build(
                email=user_info["kakao_account"]["email"],
                social_id=str(user_info["id"]),
                name=user_info["properties"]["nickname"],
            )
        elif social_type == "naver":
            user_info = await self.get_naver_user_info(access_token)
            return SocialUserInfo.build(
                email=user_info["response"]["email"],
                social_id=user_info["response"]["id"],
                name=user_info["response"]["name"],
            )
        else:
            raise ValueError(f"Unsupported social login type: {social_type}")

    @staticmethod
    def generate_access_token(user_id: int, user_type: str) -> str:
        payload: JwtPayloadTypedDict = {
            "user_id": user_id,  # 사용자 고유 ID
            "user_type": user_type,  # 사용자 역할 (예: guest, admin)
            "isa": str(time.time()),
            "iss": "oz-coding",
        }
        return jwt.encode(
            payload=dict(payload),
            key=JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    @staticmethod
    def generate_refresh_token(user_id: int, user_type: str) -> str:
        payload: JwtPayloadTypedDict = {
            "user_id": user_id,  # 사용자 고유 ID
            "user_type": user_type,  # 사용자 역할 (예: guest, admin)
            "isa": str(time.time()),
            "iss": "oz-coding",
        }
        return jwt.encode(
            payload=dict(payload),
            key=JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    async def get_access_token(self, code: str, social_type: str) -> str:
        if social_type == "kakao":
            return await self._get_kakao_access_token(code)
        elif social_type == "naver":
            return await self._get_naver_access_token(code)
        else:
            raise ValueError(f"Unsupported social login type: {social_type}")

    @staticmethod
    async def _get_kakao_access_token(code: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(KAKAO_TOKEN_URL, data=data)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="카카오 토큰 요청 실패")

            tokens: dict[str, Any] = response.json()
            access_token = tokens.get("access_token")

            if not access_token or not isinstance(access_token, str):
                raise HTTPException(
                    status_code=400,
                    detail="Kakao access token is missing or invalid.",
                )
            return str(access_token)

    @staticmethod
    async def _get_naver_access_token(code: str) -> str:
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "redirect_uri": settings.NAVER_REDIRECT_URI,
            "code": code,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(NAVER_TOKEN_URL, data=payload)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="네이버 토큰 요청 실패")

            tokens = response.json()
            access_token = tokens.get("access_token")

            if not access_token or not isinstance(access_token, str):
                raise HTTPException(
                    status_code=400,
                    detail="Kakao access token is missing or invalid.",
                )
            return str(access_token)

    @staticmethod
    async def get_kakao_user_info(access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(KAKAO_USER_INFO_URL, headers=headers)
            response.raise_for_status()
            return response.json()  # type: ignore

    @staticmethod
    async def get_naver_user_info(access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(NAVER_USER_INFO_URL, headers=headers)
            response.raise_for_status()
            return response.json()  # type: ignore

    async def refresh_access_token(self, access_token: str) -> JwtTokenResponseDTO:

        payload = self._decode_token(access_token)

        user_id = payload.get("user_id")
        user = await User.get(id=user_id)

        refresh_token = user.refresh_token_id
        payload = self._decode_token(refresh_token)

        if not self.is_valid_refresh_token(payload):
            raise HTTPException(status_code=401, detail="Refresh token has expired")

        return JwtTokenResponseDTO.build(
            access_token=self.generate_access_token(
                user_id=user.id,
                user_type=user.user_type,
            ),
            user_id=user.id,
            name=user.name,
        )

    @staticmethod
    def _decode_token(token: str) -> JwtPayloadTypedDict:
        payload = jwt.decode(
            jwt=token,
            key=JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        return cast(JwtPayloadTypedDict, payload)

    @staticmethod
    def is_valid_access_token(payload: JwtPayloadTypedDict) -> bool:
        return time.time() < float(payload["isa"]) + JWT_EXPIRY_SECONDS

    @staticmethod
    def is_valid_refresh_token(payload: JwtPayloadTypedDict) -> bool:
        return time.time() < float(payload["isa"]) + JWT_REFRESH_EXPIRY_SECONDS

    #
    # @staticmethod
    # def _get_access_jwt(
    #     auth_header: HTTPAuthorizationCredentials = HTTPBearer(auto_error=False),
    # ):
    #     if auth_header is None:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="JWT access not provided",
    #         )
    #     return auth_header.credentials
    #
    # @staticmethod
    # def _get_refresh_jwt(
    #     auth_header: HTTPAuthorizationCredentials | None = APIKeyHeader(name="X-Refresh-Token", auto_error=False),
    # ):
    #     if auth_header is None:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="JWT refresh not provided",
    #         )
    #     return auth_header
    #
    # @staticmethod
    # def get_username(
    #     access_token_in_header: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    #     refresh_token_in_header: str | None = Depends(APIKeyHeader(name="X-Refresh-Token", auto_error=False)),
    # ):
    #     access_token = AuthenticateService._get_access_jwt(access_token_in_header)
    #     access_token_payload = AuthenticateService._decode_token(access_token)
    #
    #     refresh_token = AuthenticateService._get_refresh_jwt(refresh_token_in_header)
    #     refresh_token_payload = AuthenticateService._decode_token(refresh_token)
    #
    #     if not AuthenticateService.is_valid_access_token(
    #         access_token_payload
    #     ) and not AuthenticateService.is_valid_refresh_token(refresh_token_payload):
    #
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Expired")
    #     return access_token_payload.get("username")
    #
    @staticmethod
    def generate_verification_code() -> str:
        return str(random.randint(100000, 999999))
