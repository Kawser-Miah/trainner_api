from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.schemas.client.billing.user_billing_schemas import (
    UserBillingHistoryData,
)
from src.service.client.billing.user_billing_history_service import (
    get_user_billing_history_service,
)

router = APIRouter(
    tags=["Client Billing"],
)


@router.get(
    settings.user_billing_history_prefix,
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Get User Billing History",
    description="Retrieve billing history, metrics, and transactions for the authenticated client.",
)
@router.get(
    f"{settings.user_billing_history_prefix}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_user_billing_history(
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    history_data = await get_user_billing_history_service(
        db=db,
        current_user=current_user,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Billing history retrieved successfully.",
        data=history_data,
    )

