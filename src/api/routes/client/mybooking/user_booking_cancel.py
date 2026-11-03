from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.mybooking.user_booking_cancel_service import (
    cancel_user_booking_service,
)

router = APIRouter(
    tags=["Client Booking & Payments"],
)


@router.post(
    f"{settings.user_booking_cancel_prefix}/{{booking_id}}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Cancel Booking",
    description="Cancel an authenticated client's confirmed service booking and issue an instant refund.",
)
@router.post(
    f"{settings.user_booking_cancel_prefix}/{{booking_id}}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def cancel_user_booking(
    booking_id: int,
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    booking = await cancel_user_booking_service(
        db=db,
        current_user=current_user,
        booking_id=booking_id,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Booking successfully cancelled and amount refunded to your account.",
        data=booking,
    )
