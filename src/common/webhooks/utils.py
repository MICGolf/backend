import hashlib
import hmac


def verify_signature(secret: str, payload: bytes, signature: str) -> bool:
    """
    Webhook 서명을 검증합니다.
    """
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected_signature, signature)
