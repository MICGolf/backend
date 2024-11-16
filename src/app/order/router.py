from fastapi import APIRouter

router = APIRouter(prefix="/order", tags=["주문"])


@router.get("")
async def get_order() -> dict[str, str]:
    return {"message": "Hello World"}
