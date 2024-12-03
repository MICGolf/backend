from pydantic import BaseModel


class JwtTokenResponseDTO(BaseModel):
    access_token: str

    @classmethod
    def build(cls, access_token: str) -> "JwtTokenResponseDTO":
        return cls(access_token=access_token)


class RefreshTokenRequest(BaseModel):
    access_token: str


class UserLoginInfoResponseDTO(BaseModel):
    login_type: list[str]  # 로그인 타입 (email, kakao, naver)
    login_id: str

    @classmethod
    def build(cls, login_type: list[str], login_id: str) -> "UserLoginInfoResponseDTO":
        return cls(
            login_type=login_type,
            login_id=login_id,
        )
