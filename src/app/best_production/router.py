from fastapi import APIRouter

router = APIRouter(prefix="/best-product", tags=["Best-Product"])


@router.get("")
async def get_best_product() -> dict[str, str]:
    return {"message": "Hello World"}
