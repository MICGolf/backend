from typing import Any

from common.exceptions.error_code import ErrorCode


class CustomException(Exception):
    def __init__(self, error_code: ErrorCode) -> None:
        self.error_code = error_code
        super().__init__(error_code.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.error_code.code,
            "message": self.error_code.message,
            "data": None,
        }

    @property
    def status_code(self) -> int:
        return self.error_code.status_code


class UserNotFoundException(CustomException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.USER_NOT_FOUND)


class InvalidPasswordException(CustomException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_PASSWORD)


class SocialLoginConflictException(CustomException):
    def __init__(self, social_login_type: str) -> None:
        super().__init__(ErrorCode.SOCIAL_LOGIN_CONFLICT)
        self.social_login_type = social_login_type

    def __str__(self) -> str:
        return f"Social login conflict detected for social type: {self.social_login_type}"


class MaxImagesPerColorExceeded(CustomException):
    def __init__(self, color_code: str, max_images: int) -> None:
        self.color_code = color_code
        self.max_images = max_images
        super().__init__(ErrorCode.MAX_IMAGES_EXCEEDED)

    def __str__(self) -> str:
        return f"Color {self.color_code} has more than the allowed {self.max_images} images."


class MaxImageSizeExceeded(CustomException):
    def __init__(self, color_code: str, max_size: int) -> None:
        self.color_code = color_code
        self.max_size = max_size
        super().__init__(ErrorCode.MAX_IMAGE_SIZE_EXCEEDED)

    def __str__(self) -> str:
        return f"Total image size for color {self.color_code} exceeds the {self.max_size // (1024 * 1024)}MB limit."


class ResetTokenExpiredException(CustomException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RESET_TOKEN_EXPIRED)


class LoginIdAlreadyTakenException(CustomException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.USER_ALREADY_EXISTS)


class UnsupportedSocialLoginTypeException(CustomException):
    def __init__(self, social_type: str) -> None:
        self.social_type = social_type
        super().__init__(ErrorCode.UNSUPPORTED_SOCIAL_LOGIN_TYPE)

    def __str__(self) -> str:
        return f"Unsupported social login type: {self.social_type}"


class SocialTokenRequestFailedException(CustomException):
    def __init__(self, social_type: str) -> None:
        self.social_type = social_type
        if social_type == "kakao":
            super().__init__(ErrorCode.KAKAO_TOKEN_REQUEST_FAILED)
        elif social_type == "naver":
            super().__init__(ErrorCode.NAVER_TOKEN_REQUEST_FAILED)  # 네이버에도 동일한 에러코드를 사용할 경우
        else:
            raise ValueError(f"Unsupported social type: {social_type}")

    def __str__(self) -> str:
        return f"Token request failed for {self.social_type.capitalize()}."


class SocialAccessTokenInvalidException(CustomException):
    def __init__(self, social_type: str) -> None:
        self.social_type = social_type
        if social_type == "kakao":
            super().__init__(ErrorCode.KAKAO_ACCESS_TOKEN_INVALID)
        elif social_type == "naver":
            super().__init__(ErrorCode.NAVER_ACCESS_TOKEN_INVALID)
        else:
            raise ValueError(f"Unsupported social type: {social_type}")

    def __str__(self) -> str:
        return f"Access token is invalid for {self.social_type.capitalize()}."


class AccessTokenExpiredException(CustomException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.ACCESS_TOKEN_EXPIRED)


class RefreshTokenExpiredException(CustomException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.REFRESH_TOKEN_EXPIRED)

    def __str__(self) -> str:
        return "The access token has expired."


class JWTAccessNotProvidedException(CustomException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.JWT_ACCESS_NOT_PROVIDED)


class InvalidTokenException(CustomException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_TOKEN)
