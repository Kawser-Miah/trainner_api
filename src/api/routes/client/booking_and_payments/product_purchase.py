from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.schemas.client.booking_and_payments.product_purchase_schemas import (
    PurchaseProductRequest,
)
from src.service.client.booking_and_payments.product_purchase_service import (
    purchase_product_service,
)

router = APIRouter(
    tags=["Client Booking & Payments"],
)

route_path = settings.product_purchase_prefix


@router.post(
    route_path,
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    summary="Purchase Digital Product",
    description="Create a new purchase order for a digital product.",
)
@router.post(
    f"{route_path}/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def purchase_product(
    payload: PurchaseProductRequest,
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    order_data = await purchase_product_service(
        payload=payload,
        current_user=current_user,
        db=db,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_201_CREATED,
        status=status.HTTP_201_CREATED,
        message="Product purchase order created successfully. Proceed to payment.",
        data=order_data.model_dump(by_alias=True),
    )

