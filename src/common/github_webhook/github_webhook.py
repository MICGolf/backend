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
        process_name = "gunicorn"

        try:
            # git pull 명령어 실행
            subprocess.run(["git", "-C", repo_path, "pull", "origin", "develop"], check=True)

            # server PID 가져오기
            result = subprocess.run(
                ["pgrep", "-f", process_name],
                check=True,
                capture_output=True,
                text=True,
            )
            pid = result.stdout.strip().splitlines()[0]     # 첫번째 PID 가져오기

            # HUP 신호 보내기
            subprocess.run(["kill", "-HUP", pid], check=True)

            return {"message": "Git pull & server reload executed successfully"}

        except subprocess.CalledProcessError as e:
            return {"error": f"Git pull failed: {e}"}

    return {"message": "No action taken"}
