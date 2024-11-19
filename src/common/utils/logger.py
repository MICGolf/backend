import logging

import os

from core.configs import Settings
from core.configs.settings import Env

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def setup_logger(
    name: str = "app_logger", settings: Settings = None, enable_tortoise_logging: bool = False
) -> logging.Logger:
    """
    로거 설정 함수.
    :param name: 로거 이름
    :param settings: Settings 객체로 환경 정보 전달
    :param enable_tortoise_logging: Tortoise ORM 쿼리 로깅 활성화 여부 (개발 환경에서만 동작)
    :return: 설정된 로거 객체
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.ENV == Env.LOCAL else logging.INFO)

    if settings.ENV != Env.LOCAL:
        log_dir = f"{settings.PROJECT_ROOT}/logs"
        os.makedirs(log_dir, exist_ok=True)

    if not logger.hasHandlers():
        if settings.ENV == Env.LOCAL:
            handler = logging.StreamHandler()
        else:
            log_file = f"{settings.PROJECT_ROOT}/logs/{name}.log"
            handler = logging.FileHandler(log_file)

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Tortoise ORM 로깅 활성화 (LOCAL 환경에서만)
    if enable_tortoise_logging and settings.ENV == Env.LOCAL:
        db_client_logger = logging.getLogger("tortoise.db_client")
        db_client_logger.setLevel(logging.DEBUG)

        if not db_client_logger.hasHandlers():
            db_handler = logging.StreamHandler()
            db_handler.setFormatter(formatter)
            db_client_logger.addHandler(db_handler)

    return logger
