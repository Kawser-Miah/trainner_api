from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.recommended_coach_service import (
    get_recommended_coach_profile_list_service,
)

router = APIRouter(
    prefix=settings.recommended_coach_profile_list_prefix,
    tags=["Client Browse Coaches"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Recommended Coach Profile List",
    description="Retrieve top recommended coach profiles for the client.",
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_recommended_coach_profile_list(
    request: Request,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    profiles = await get_recommended_coach_profile_list_service(
        db=db,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Recommended coach profiles retrieved successfully.",
        data=profiles,
    )
