from fastapi import APIRouter

router = APIRouter(prefix="/product", tags=["상품"])


@router.get("")
async def get_product() -> dict[str, str]:
    return {"message": "Hello World"}
