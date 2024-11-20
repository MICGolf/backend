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

    class Config:
        env_file = f".env.{os.getenv('ENV', 'local')}"  # 로드할 .env 파일 결정
        env_file_encoding = "utf-8"

    @property
    def UPLOAD_DIR(self) -> str:
        if self.ENV == Env.LOCAL:
            return self.LOCAL_UPLOAD_DIR
        else:
            return self.ENDPOINT_URL
