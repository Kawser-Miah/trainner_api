from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.accounts.user import User
from src.schemas.auth.change_password import ChangePasswordRequest
from src.service.auth.change_password import change_password


router = APIRouter(
    prefix=settings.change_password_prefix,
    tags=["Change Password"],
)


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    response_model_exclude_none=True,
)
@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def change_password_account(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await change_password(
        db=db,
        user=current_user,
        request=request,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Password changed successfully.",
    )
