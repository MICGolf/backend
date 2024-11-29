import subprocess

from fastapi import APIRouter, Request

router = APIRouter(prefix="", tags=["github webhook"])


@router.post("")
async def webhook(request: Request) -> dict[str, str]:
    payload = await request.json()

    # Push 이벤트 및 develop 브랜치 확인
    if payload.get("ref") == "refs/heads/develop":
        # Git pull 명령 실행
        repo_path = "/root/backend/src"  # 서버의 레포지토리 경로
        try:
            subprocess.run(["git", "-C", repo_path, "pull", "origin", "develop"], check=True)
            return {"message": "Git pull executed successfully"}
        except subprocess.CalledProcessError as e:
            return {"error": f"Git pull failed: {e}"}

    return {"message": "No action taken"}
