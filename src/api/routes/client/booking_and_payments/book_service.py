from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.schemas.client.booking_and_payments.booking_schemas import (
    BookServiceRequest,
)
from src.service.client.booking_and_payments.book_service_service import (
    book_service_service,
)

router = APIRouter(
    tags=["Client Booking & Payments"],
)


@router.post(
    settings.book_service_prefix,
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    summary="Book a Coach Service",
    description="Create a new service order for booking a coach session.",
)
@router.post(
    f"{settings.book_service_prefix}/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def book_service(
    payload: BookServiceRequest,
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    order_data = await book_service_service(
        payload=payload,
        current_user=current_user,
        db=db,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_201_CREATED,
        status=status.HTTP_201_CREATED,
        message="Service order created successfully.",
        data=order_data,
    )
