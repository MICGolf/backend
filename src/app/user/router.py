from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["유저"])


@router.get("")
async def get_user() -> dict[str, str]:
    return {"message": "Hello World"}
