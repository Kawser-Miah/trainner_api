from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.schemas.client.myproduct.user_product_schemas import (
    UserPurchasedProductItem,
)
from src.service.client.myproduct.user_product_detail_service import (
    get_user_product_detail_service,
)

router = APIRouter(
    tags=["Client Purchased Products"],
)


@router.get(
    f"{settings.user_product_detail_prefix}/{{product_order_id}}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get User Product Detail",
    description="Retrieve details of a purchased digital product order.",
)
@router.get(
    f"{settings.user_product_detail_prefix}/{{product_order_id}}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_user_product_detail(
    product_order_id: int,
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    product_detail = await get_user_product_detail_service(
        db=db,
        current_user=current_user,
        product_order_id=product_order_id,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Product booking details retrieved successfully.",
        data=product_detail,
    )

