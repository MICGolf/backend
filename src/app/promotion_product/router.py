from fastapi import APIRouter

router_best = APIRouter(prefix="/best-product", tags=["Best-Product"])
router_mds = APIRouter(prefix="/mds-choice", tags=["Md's Choice"])


@router_best.get("")
async def get_best_product() -> dict[str, str]:
    return {"message": "Hello World"}


@router_mds.get("")
async def get_mds_choice() -> dict[str, str]:
    return {"message": "Hello World"}
