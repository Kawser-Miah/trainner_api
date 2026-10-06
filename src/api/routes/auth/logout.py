from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.accounts.user import User
from src.schemas.auth.logout import LogoutRequest, LogoutResponse
from src.service.auth.logout import logout_user


router = APIRouter(
    prefix=settings.logout_prefix,
    tags=["Logout"],
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse,
    response_model_exclude_none=True,
    summary="User Logout",
    description="Logs out the user by verifying the bearer access token and the provided refresh token.",
)
@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await logout_user(
        db=db,
        user=current_user,
        refresh_token=request.refresh,
    )

    return LogoutResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Logged out successfully.",
    )
