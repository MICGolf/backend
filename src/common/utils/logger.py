import logging
import os
from typing import Optional

from core.configs import Settings  # type: ignore
from core.configs.settings import Env

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def setup_logger(
    name: str = "app_logger", settings: Optional[Settings] = None, enable_tortoise_logging: bool = False
) -> logging.Logger:
    if not settings:
        raise ValueError("Settings 객체는 None일 수 없습니다.")

    logger = logging.getLogger(name)
    is_local_env = settings.ENV == Env.LOCAL

    logger.setLevel(logging.DEBUG if is_local_env else logging.INFO)

    if not is_local_env:
        log_dir = os.path.join(settings.PROJECT_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

    if not logger.hasHandlers():
        if is_local_env:
            handler: logging.Handler = logging.StreamHandler()
        else:
            log_file = os.path.join(settings.PROJECT_ROOT, "logs", f"{name}.log")
            handler = logging.FileHandler(log_file)

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if enable_tortoise_logging and is_local_env:
        db_client_logger = logging.getLogger("tortoise.db_client")
        db_client_logger.setLevel(logging.DEBUG)

        if not db_client_logger.hasHandlers():
            db_handler = logging.StreamHandler()
            db_handler.setFormatter(formatter)
            db_client_logger.addHandler(db_handler)

    return logger
