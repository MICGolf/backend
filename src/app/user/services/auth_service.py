import random
import time
from typing import Any, Optional, cast

import bcrypt
import httpx
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBasic, HTTPBearer

from app.user.dtos.auth_dto import JwtPayloadTypedDict, ResetTokenPayloadTypedDict, SocialUserInfo
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
    PASSWORD_RESET_TOKEN_EXPIRY_SECONDS,
)
from common.exceptions.custom_exceptions import (
    AccessTokenExpiredException,
    InvalidPasswordException,
    InvalidTokenException,
    JWTAccessNotProvidedException,
    RefreshTokenExpiredException,
    SocialAccessTokenInvalidException,
    SocialTokenRequestFailedException,
    UnsupportedSocialLoginTypeException,
)
from core.configs import settings

basic_auth = HTTPBasic()


class AuthenticateService:
    @staticmethod
    async def hash_password(plain_password: str) -> str:
        plain_password_bytes = plain_password.encode("UTF-8")
        hashed_password = bcrypt.hashpw(plain_password_bytes, bcrypt.gensalt())
        return hashed_password.decode("UTF-8")

    @staticmethod
    async def check_password(input_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            input_password.encode("UTF-8"),
            hashed_password.encode("UTF-8"),
        )

    async def verify_password(self, input_password: str, stored_hashed_password: str) -> bool:
        is_valid = await self.check_password(input_password, stored_hashed_password)

        if not is_valid:
            raise InvalidPasswordException()

        return True

    async def get_social_user_info(self, access_token: str, social_type: str) -> SocialUserInfo:
        if social_type == "kakao":
            user_info = await self._get_kakao_user_info(access_token)
            return SocialUserInfo.build(
                email=user_info["kakao_account"]["email"],
                social_id=str(user_info["id"]),
                name=user_info["properties"]["nickname"],
            )
        elif social_type == "naver":
            user_info = await self._get_naver_user_info(access_token)
            return SocialUserInfo.build(
                email=user_info["response"]["email"],
                social_id=user_info["response"]["id"],
                name=user_info["response"]["name"],
            )
        else:
            raise UnsupportedSocialLoginTypeException(social_type=social_type)

    @staticmethod
    async def generate_access_token(user_id: int, user_type: str, user_name: str) -> str:
        payload: JwtPayloadTypedDict = {
            "user_id": user_id,  # 사용자 고유 ID
            "user_type": user_type,  # 사용자 역할 (예: guest, admin)
            "user_name": user_name,
            "isa": str(time.time()),
            "iss": "oz-coding",
        }
        return jwt.encode(
            payload=dict(payload),
            key=JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    @staticmethod
    async def generate_refresh_token(user_id: int, user_type: str, user_name: str) -> str:
        payload: JwtPayloadTypedDict = {
            "user_id": user_id,  # 사용자 고유 ID
            "user_type": user_type,  # 사용자 역할 (예: guest, admin)
            "user_name": user_name,
            "isa": str(time.time()),
            "iss": "oz-coding",
        }
        return jwt.encode(
            payload=dict(payload),
            key=JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    @staticmethod
    async def generate_reset_token(user_id: int, user_name: str) -> str:
        payload: ResetTokenPayloadTypedDict = {
            "user_id": user_id,
            "user_name": user_name,
            "isa": str(time.time()),
            "iss": "oz-coding",
        }
        return jwt.encode(
            payload=dict(payload),
            key=JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    async def get_access_token(self, code: str, social_type: str, state: Optional[str] = None) -> str:
        if social_type == "kakao":
            return await self._get_kakao_access_token(code=code)
        elif social_type == "naver":
            return await self._get_naver_access_token(code=code, state=state)
        else:
            raise UnsupportedSocialLoginTypeException(social_type=social_type)

    async def _get_kakao_access_token(self, code: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }

        response = await self._request_token(url=KAKAO_TOKEN_URL, data=data)

        if response.status_code != 200:
            raise SocialTokenRequestFailedException(social_type="kakao")

        tokens: dict[str, Any] = response.json()
        access_token = tokens.get("access_token")

        if not self._is_valid_token_format(access_token=access_token):
            raise SocialAccessTokenInvalidException(social_type="kakao")

        return str(access_token)

    async def _get_naver_access_token(self, code: str, state: Optional[str] = None) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "redirect_uri": settings.NAVER_REDIRECT_URI,
            "code": code,
            "state": state,
        }
        response = await self._request_token(url=NAVER_TOKEN_URL, data=data)

        if response.status_code != 200:
            raise SocialTokenRequestFailedException(social_type="naver")

        tokens = response.json()
        access_token = tokens.get("access_token")

        if not self._is_valid_token_format(access_token=access_token):
            raise SocialAccessTokenInvalidException(social_type="naver")

        return str(access_token)

    @staticmethod
    async def _request_token(url: str, data: dict[str, Any]) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            return await client.post(url, data=data)

    @staticmethod
    def _is_valid_token_format(access_token: Any) -> bool:
        return isinstance(access_token, str) and bool(access_token)

    @staticmethod
    async def _get_kakao_user_info(access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(KAKAO_USER_INFO_URL, headers=headers)
            response.raise_for_status()
            return response.json()  # type: ignore

    @staticmethod
    async def _get_naver_user_info(access_token: str) -> dict[str, Any]:
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
            raise RefreshTokenExpiredException()

        return JwtTokenResponseDTO.build(
            access_token=await self.generate_access_token(
                user_id=user.id,
                user_type=user.user_type,
                user_name=user.name,
            ),
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
    async def _decode_reset_token(token: str) -> ResetTokenPayloadTypedDict:
        payload = jwt.decode(
            jwt=token,
            key=JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        return cast(ResetTokenPayloadTypedDict, payload)

    def is_valid_access_token(self, payload: JwtPayloadTypedDict) -> bool:
        jwt_token_expiry = self._jwt_expiry_seconds()
        return time.time() < float(payload["isa"]) + jwt_token_expiry

    @staticmethod
    def _jwt_expiry_seconds() -> int:
        return JWT_EXPIRY_SECONDS

    def is_valid_refresh_token(self, payload: JwtPayloadTypedDict) -> bool:
        refresh_token_expiry = self._jwt_refresh_expiry_seconds()
        return time.time() < float(payload["isa"]) + refresh_token_expiry

    @staticmethod
    def _jwt_refresh_expiry_seconds() -> int:
        return JWT_REFRESH_EXPIRY_SECONDS

    @staticmethod
    def is_valid_reset_token(payload: ResetTokenPayloadTypedDict) -> bool:
        return time.time() < float(payload["isa"]) + PASSWORD_RESET_TOKEN_EXPIRY_SECONDS

    @staticmethod
    def _get_access_jwt(
        auth_header: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    ) -> str:
        if auth_header is None or not auth_header.credentials:
            raise JWTAccessNotProvidedException()
        return auth_header.credentials

    def get_user_id(
        self,
        access_token_in_header: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    ) -> int:
        access_token = self._get_access_jwt(access_token_in_header)
        access_token_payload = self._decode_token(access_token)

        if not self.is_valid_access_token(access_token_payload):
            raise AccessTokenExpiredException()

        user_id = access_token_payload.get("user_id")

        if user_id is None:
            raise InvalidTokenException()

        return user_id

    @staticmethod
    async def generate_verification_code() -> str:
        return str(random.randint(100000, 999999))


security = HTTPBearer(auto_error=False)


# 헬퍼 함수 - 토큰만 뽑아오는 함수
def get_token_from_header(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials is None:
        raise JWTAccessNotProvidedException()
    return credentials.credentials
