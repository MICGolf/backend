from enum import Enum


class ErrorCode(Enum):
    USER_NOT_FOUND = (4001, "User not found")
    INVALID_PASSWORD = (4002, "Invalid password")
    SOCIAL_LOGIN_CONFLICT = (4003, "Social login conflict detected")
    MAX_IMAGES_EXCEEDED = (4004, "Maximum number of images for this color exceeded")
    MAX_IMAGE_SIZE_EXCEEDED = (4005, "Maximum image size for this color exceeded")
    RESET_TOKEN_EXPIRED = (4006, "Reset token expired.")

    def __init__(self, code: int, message: str) -> None:
        self._code = code
        self._message = message

    @property
    def code(self) -> int:
        return self._code

    @property
    def message(self) -> str:
        return self._message
