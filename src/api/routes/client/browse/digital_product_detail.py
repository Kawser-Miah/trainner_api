from fastapi import APIRouter, Depends, Path, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.digital_product_detail_service import (
    get_digital_product_detail_service,
)

router = APIRouter(
    prefix=settings.digital_product_detail_prefix,
    tags=["Client Browse Digital Products"],
)


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Digital Product Detail",
    description="Retrieve digital product details including other products by the same coach.",
)
@router.get(
    "/{product_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_digital_product_detail(
    product_id: int = Path(..., description="Digital Product ID"),
    request: Request = None,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    detail = await get_digital_product_detail_service(
        product_id=product_id,
        db=db,
        current_user=current_user,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Digital product details retrieved successfully.",
        data=detail,
    )
