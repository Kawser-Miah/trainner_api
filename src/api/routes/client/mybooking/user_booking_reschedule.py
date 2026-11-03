from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.schemas.client.booking_and_payments.user_booking_schemas import (
    RescheduleBookingRequest,
)
from src.service.client.mybooking.user_booking_reschedule_service import (
    reschedule_user_booking_service,
)

router = APIRouter(
    tags=["Client Booking & Payments"],
)


@router.post(
    f"{settings.user_booking_reschedule_prefix}/{{booking_id}}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Reschedule Booking",
    description="Reschedule an authenticated client's confirmed service booking.",
)
@router.post(
    f"{settings.user_booking_reschedule_prefix}/{{booking_id}}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def reschedule_user_booking(
    booking_id: int,
    payload: RescheduleBookingRequest,
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    booking = await reschedule_user_booking_service(
        db=db,
        current_user=current_user,
        booking_id=booking_id,
        payload=payload,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Booking rescheduled successfully.",
        data=booking,
    )

