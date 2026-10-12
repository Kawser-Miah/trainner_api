from fastapi import APIRouter, Depends, Path, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.user_service_detail_service import get_user_service_detail_service

router = APIRouter(
    prefix=settings.user_service_detail_prefix,
    tags=["Client Browse Services"],
)


@router.get(
    "/{service_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="User Service Detail",
    description="Retrieve service details including other sessions by the same coach.",
)
@router.get(
    "/{service_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_user_service_detail(
    service_id: int = Path(..., description="Service ID"),
    request: Request = None,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    detail = await get_user_service_detail_service(
        service_id=service_id,
        db=db,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Service details retrieved successfully.",
        data=detail,
    )
