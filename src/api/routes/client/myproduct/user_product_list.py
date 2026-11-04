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
from src.service.client.myproduct.user_product_list_service import (
    get_user_purchased_products_service,
)

router = APIRouter(
    tags=["Client Purchased Products"],
)


@router.get(
    settings.user_product_list_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get User Purchased Products",
    description="Retrieve all digital products purchased by the authenticated user.",
)
@router.get(
    f"{settings.user_product_list_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_user_product_list(
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    products = await get_user_purchased_products_service(
        db=db,
        current_user=current_user,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="User purchased products retrieved successfully.",
        data=products,
    )
