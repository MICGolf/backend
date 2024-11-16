from fastapi import APIRouter

router = APIRouter(prefix="/mds-choice", tags=["Md's Choice"])


@router.get("")
async def get_mds_choice() -> dict[str, str]:
    return {"message": "Hello World"}
