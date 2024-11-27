from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequestDTO(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    login_id: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)
    user_type: Optional[str] = Field("guest", max_length=10)  # guest, admin
    social_login_type: Optional[str] = Field(None, max_length=50)
    social_id: Optional[str] = None


class UserResponseDTO(BaseModel):
    id: int
    name: str
    email: str
    login_id: str
    status: bool

    class Config:
        orm_mode = True


class OauthRequestDTO(BaseModel):
    social_id: str
