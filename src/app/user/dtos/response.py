from pydantic import BaseModel


class JwtTokenResponseDTO(BaseModel):
    access_token: str
    user_id: int
    name: str

    @classmethod
    def build(cls, access_token: str, user_id: int, name: str) -> "JwtTokenResponseDTO":
        return cls(
            access_token=access_token,
            user_id=user_id,
            name=name,
        )


class RefreshTokenRequest(BaseModel):
    access_token: str


class UserLoginInfoResponseDTO(BaseModel):
    login_type: str  # 로그인 타입 (normal or social)
    social_type: str  # 소셜 로그인 타입 (ex. naver, kakao, none)
    email: str  # 이메일

    @classmethod
    def build(cls, login_type: str, social_type: str, email: str) -> "UserLoginInfoResponseDTO":
        return cls(
            login_type=login_type,
            social_type=social_type,
            email=email,
        )
