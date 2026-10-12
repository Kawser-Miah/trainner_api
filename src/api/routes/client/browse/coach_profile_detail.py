from fastapi import APIRouter, Depends, Path, Request, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import require_client_role
from src.models.accounts.user import User
from src.service.client.browse.coach_profile_detail_service import get_coach_profile_detail_service

router = APIRouter(
    prefix=settings.client_coach_profile_detail_prefix,
    tags=["Client Browse Coaches"],
)


@router.get(
    "/{coach_profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    summary="Coach Profile Detail",
    description="Retrieve full details for a specific coach profile.",
)
@router.get(
    "/{coach_profile_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_coach_profile_detail(
    coach_profile_id: int = Path(..., description="Coach Profile ID"),
    request: Request = None,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    profile_detail = await get_coach_profile_detail_service(
        coach_profile_id=coach_profile_id,
        db=db,
        request=request,
    )
    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Coach profile details retrieved successfully.",
        data=profile_detail,
    )
