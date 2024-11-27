import subprocess
import hmac
import hashlib
from fastapi import APIRouter, HTTPException, Request
import logging

logger = logging.getLogger("webhook_logger")

router = APIRouter()

SECRET = "2f8e0d9a47f3c0196fbae7c1b084e33d3f6576ad20cd8cba8c0f75613ae2c42b"
ALLOWED_BRANCHES = ["refs/heads/develop"]


def verify_signature(secret: str, payload: bytes, signature: str) -> bool:
    """
    GitHub Webhook 서명을 검증합니다.
    """
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected_signature, signature)


@router.post("/")
async def github_webhook(request: Request) -> dict[str, str]:
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logger.warning("Missing signature header")
        raise HTTPException(status_code=400, detail="Missing signature header")

    payload = await request.body()

    # 서명 검증
    if not verify_signature(SECRET, payload, signature):
        logger.warning(f"Invalid signature: {signature}")
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        payload_json = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # 브랜치 확인
    branch_ref = payload_json.get("ref")  # 예: "refs/heads/develop"
    if branch_ref in ALLOWED_BRANCHES:
        try:
            subprocess.run(["git", "pull"], cwd="/path/to/your/backend", check=True)
            with open("/tmp/gunicorn.pid") as pid_file:
                pid = pid_file.read().strip()
            subprocess.run(["kill", "-HUP", pid], check=True)
            return {"status": "success", "message": "Code pulled and server reloaded"}
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")

    return {"status": "ignored", "message": f"Push to {branch_ref} ignored"}
