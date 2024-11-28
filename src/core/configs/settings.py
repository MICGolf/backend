import os
from enum import StrEnum

from pydantic_settings import BaseSettings


class Env(StrEnum):
    LOCAL = "local"
    STAGE = "stage"
    PROD = "prod"


class Settings(BaseSettings):
    ENV: Env = Env.LOCAL
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "1234"
    DB_NAME: str = "micgolf"

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

    LOCAL_UPLOAD_DIR: str = os.path.join(PROJECT_ROOT, "uploads")

    AWS_ACCESS_KEY: str = "your-access-key"
    AWS_SECRET_KEY: str = "your-secret-key"
    ENDPOINT_URL: str = "https://kr.object.ncloudstorage.com"
    REGION_NAME: str = "your-region-name"
    AWS_STORAGE_BUCKET_NAME: str = "your-bucket-name"

    JWT_SECRET_KEY: str = "your-jwt-secret-key"

    # NAVER CLOUD SMS settings
    SMS_SERVICE_TYPE: str = "ncp"
    SMS_SERVICE_ID: str = "SMS_SERVICE_ID"
    NCP_API_KEY: str = "NCP_API_KEY"
    NCP_API_SECRET: str = "NCP_API_SECRET"
    NCP_SMS_FROM_NUMBER: str = "NCP_SMS_FROM_NUMBER"

    # KAKAO LOGIN settings
    KAKAO_CLIENT_ID: str = "KAKAO_CLIENT_ID"
    KAKAO_CLIENT_SECRET: str = "KAKAO_CLIENT_SECRET"
    KAKAO_REDIRECT_URI: str = "KAKAO_REDIRECT_URI"

    # naver login settings
    NAVER_CLIENT_ID: str = "NAVER_CLIENT_ID"
    NAVER_CLIENT_SECRET: str = "NAVER_CLIENT_SECRET"
    NAVER_REDIRECT_URI: str = "NAVER_REDIRECT_URI"

    # Email settings (SMTP)
    EMAIL_SERVICE_TYPE: str = "smtp"
    SMTP_HOST: str = "smtp.example.com"  # SMTP 서버 주소
    SMTP_PORT: int = 587  # SMTP 서버 포트
    SMTP_USER: str = "your_email@example.com"  # SMTP 사용자명
    SMTP_PASSWORD: str = "your_email_password"  # SMTP 비밀번호

    class Config:
        env_file = f".env.{os.getenv('ENV', 'local')}"
        env_file_encoding = "utf-8"

    @property
    def UPLOAD_DIR(self) -> str:
        if self.ENV == Env.LOCAL:
            return self.LOCAL_UPLOAD_DIR
        else:
            return self.ENDPOINT_URL
