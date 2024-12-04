import time

import jwt


def generate_mock_jwt(payload: dict[str, str | int], secret_key: str = "your-jwt-secret-key") -> str:
    # 기본 필드 추가
    payload.setdefault("isa", int(time.time()))  # 발행 시간
    payload.setdefault("user_type", "guest")  # 사용자 타입
    return jwt.encode(payload, secret_key, algorithm="HS256")
