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
