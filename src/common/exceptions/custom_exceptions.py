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


class MaxImagesPerColorExceeded(CustomException):
    def __init__(self, color_code: str, max_images: int) -> None:
        self.color_code = color_code
        self.max_images = max_images
        super().__init__(ErrorCode.MAX_IMAGES_EXCEEDED)


class MaxImageSizeExceeded(CustomException):
    def __init__(self, color_code: str, max_size: int) -> None:
        self.color_code = color_code
        self.max_size = max_size
        super().__init__(ErrorCode.MAX_IMAGE_SIZE_EXCEEDED)


class ResetTokenExpiredException(CustomException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RESET_TOKEN_EXPIRED)
