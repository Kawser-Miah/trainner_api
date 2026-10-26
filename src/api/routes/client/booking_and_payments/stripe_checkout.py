from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.schemas.client.booking_and_payments.stripe_schemas import (
    CreateCheckoutSessionRequest,
)
from src.service.client.booking_and_payments.stripe_service import (
    create_stripe_checkout_session_service,
)

router = APIRouter(
    tags=["Client Booking & Payments"],
)

route_path = f"{settings.stripe_prefix}{settings.create_checkout_session_prefix}"


@router.post(
    route_path,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Create Stripe Checkout Session",
    description="Generate a Stripe checkout session URL for paying for a booking.",
)
@router.post(
    f"{route_path}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def create_checkout_session(
    payload: CreateCheckoutSessionRequest,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    result = await create_stripe_checkout_session_service(
        payload=payload,
        current_user=current_user,
        db=db,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message=result.message,
        data=result.data.model_dump(),
    )
