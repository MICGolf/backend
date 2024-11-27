import hmac
import hashlib

from fastapi import APIRouter, Request, HTTPException
from common.webhooks.utils import verify_signature
import subprocess

router = APIRouter()

SECRET = "2f8e0d9a47f3c0196fbae7c1b084e33d3f6576ad20cd8cba8c0f75613ae2c42b"  # GitHub Webhook 비밀 토큰


@router.post("/")
async def github_webhook(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature header")

    payload = await request.body()

    # 서명 검증
    if not verify_signature(SECRET, payload, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # JSON 파싱
    payload_json = await request.json()

    # 브랜치 확인
    branch_ref = payload_json.get("ref")  # 예: "refs/heads/develop"
    if branch_ref == "refs/heads/develop":
        # develop 브랜치에 push된 경우
        subprocess.run(["git", "pull"], cwd="/path/to/your/backend")
        subprocess.run(["kill", "-HUP", "$(pidof gunicorn)"], shell=True)
        return {"status": "success", "message": "Code pulled and server reloaded"}

    # 다른 브랜치일 경우
    return {"status": "ignored", "message": f"Push to {branch_ref} ignored"}