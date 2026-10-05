from fastapi import APIRouter, Depends, status

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.dependencies import get_current_user
from src.models.accounts.user import User
from src.schemas.auth.me import UserProfileResponse
from src.service.auth.me import get_user_profile


router = APIRouter(
    prefix=settings.me_prefix,
    tags=["User Profile"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    profile = get_user_profile(user=current_user)

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Profile retrieved successfully.",
        data=profile,
    )
