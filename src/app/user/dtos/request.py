from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class UserCreateRequestDTO(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    login_id: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)
    password2: str = Field(..., min_length=6)

    @model_validator(mode="after")
    def validate_passwords(self) -> "ResetPasswordRequest":
        if self.password != self.password2:
            raise ValueError("The passwords do not match.")

        if not self.is_valid_password(self.password):
            raise ValueError(
                "Password must be at least 8 characters long and include uppercase, lowercase, digits, and special characters."
            )

        return self

    @staticmethod
    def is_valid_password(password: Optional[str]) -> bool:
        if password is None:
            return False
        return (
            len(password) >= 8
            and any(c.isdigit() for c in password)
            and any(c.islower() for c in password)
            and any(c.isupper() for c in password)
        )


class UserLoginRequestDTO(BaseModel):
    login_id: str
    password: str


class OauthRequestDTO(BaseModel):
    social_id: str


class PasswordResetRequestDTO(BaseModel):
    name: str
    login_id: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    new_password2: str

    @model_validator(mode="after")
    def validate_passwords(self) -> "ResetPasswordRequest":
        if self.new_password != self.new_password2:
            raise ValueError("The passwords do not match.")

        if not self.is_valid_password(self.new_password):
            raise ValueError(
                "Password must be at least 8 characters long and include uppercase, lowercase, digits, and special characters."
            )

        return self

    @staticmethod
    def is_valid_password(password: Optional[str]) -> bool:
        if password is None:
            return False
        return (
            len(password) >= 8
            and any(c.isdigit() for c in password)
            and any(c.islower() for c in password)
            and any(c.isupper() for c in password)
        )
