from fastapi import APIRouter

router = APIRouter(prefix="/banner", tags=["배너"])


@router.get("")
async def get_banner() -> dict[str, str]:
    return {"message": "Hello World"}
