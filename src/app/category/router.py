from fastapi import APIRouter

router = APIRouter(prefix="/category", tags=["카테고리"])


@router.get("")
async def get_category() -> dict[str, str]:
    return {"message": "Hello World"}
