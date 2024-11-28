from typing import TypedDict

from pydantic import BaseModel


class JwtPayloadTypedDict(TypedDict):
    user_id: int
    user_type: str
    isa: str
    iss: str


class ResetTokenPayloadTypedDict(TypedDict):
    user_id: int
    user_name: str
    isa: str
    iss: str


class SocialUserInfo(BaseModel):
    social_id: str
    email: str
    name: str

    @classmethod
    def build(cls, social_id: str, email: str, name: str) -> "SocialUserInfo":
        return cls(social_id=social_id, email=email, name=name)
