from fastapi import APIRouter

router = APIRouter(prefix="/cart", tags=["장바구니"])


@router.get("")
async def get_cart() -> dict[str, str]:
    return {"message": "Hello World"}
