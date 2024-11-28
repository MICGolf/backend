from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel


class AddPromotionRequest(BaseModel):
    promotion_type: str
    is_active: bool
    product_code: str

    def validate_promotion_type(self) -> None:
        if self.promotion_type not in ["best", "md_pick"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid promotion type '{self.promotion_type}'. Allowed types are 'best' or 'md_pick'.",
            )


class UpdatePromotionRequest(BaseModel):
    product_code: str
    promotion_type: str
    is_active: bool
    new_promotion_type: Optional[str] = None
    new_is_active: Optional[bool] = None

    def validate_promotion_type(self) -> None:
        if self.promotion_type not in ["best", "md_pick"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid promotion type '{self.promotion_type}'. Allowed types are 'best' or 'md_pick'.",
            )

        if self.new_promotion_type not in ["best", "md_pick"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid promotion type '{self.new_promotion_type}'. Allowed types are 'best' or 'md_pick'.",
            )


class DeletePromotionRequest(BaseModel):
    product_code: str
    promotion_type: str

    def validate_promotion_type(self) -> None:
        if self.promotion_type not in ["best", "md_pick"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid promotion type '{self.promotion_type}'. Allowed types are 'best' or 'md_pick'.",
            )
