from core.configs import settings

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_SECONDS = 24 * 60 * 60  # 하루: 24시간 * 60분 * 60초
JWT_REFRESH_EXPIRY_SECONDS = 30 * 24 * 60 * 60  # 한 달 : 30일 * 24시간 * 60분 * 60초


KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_USER_INFO_URL = "https://openapi.naver.com/v1/nid/me"
