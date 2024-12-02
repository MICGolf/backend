from enum import Enum


class ErrorCode(Enum):
    # 사용자 관련 에러 (1000 ~ 1999)
    USER_NOT_FOUND = (1001, "User not found", 404)
    INVALID_PASSWORD = (1002, "Invalid password", 400)
    USER_ALREADY_EXISTS = (1003, "User already exists", 409)

    # 소셜 로그인 관련 에러 (2000 ~ 2999)
    SOCIAL_LOGIN_CONFLICT = (2001, "Social login conflict detected", 409)
    UNSUPPORTED_SOCIAL_LOGIN_TYPE = (2002, "Unsupported social login type", 400)
    KAKAO_TOKEN_REQUEST_FAILED = (2003, "Kakao token request failed", 500)
    KAKAO_ACCESS_TOKEN_INVALID = (2004, "Kakao access token is missing or invalid", 400)
    NAVER_TOKEN_REQUEST_FAILED = (2005, "Naver token request failed", 500)
    NAVER_ACCESS_TOKEN_INVALID = (2006, "Naver access token is missing or invalid", 400)

    # 파일 관련 에러 (3000 ~ 3999)
    MAX_IMAGES_EXCEEDED = (3001, "Maximum number of images for this color exceeded", 400)
    MAX_IMAGE_SIZE_EXCEEDED = (3002, "Maximum image size for this color exceeded", 400)

    # 토큰 관련 에러 (4000 ~ 4999)
    RESET_TOKEN_EXPIRED = (4001, "Reset token expired", 400)
    ACCESS_TOKEN_EXPIRED = (4002, "Access token has expired.", 401)
    REFRESH_TOKEN_EXPIRED = (4003, "Refresh token has expired.", 401)
    JWT_ACCESS_NOT_PROVIDED = (4004, "JWT access token not provided.", 401)
    INVALID_TOKEN = (4005, "Invalid token or user ID not found in token.", 401)

    def __init__(self, code: int, message: str, status_code: int) -> None:
        self._code = code
        self._message = message
        self._status_code = status_code

    @property
    def code(self) -> int:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    @property
    def status_code(self) -> int:
        return self._status_code
