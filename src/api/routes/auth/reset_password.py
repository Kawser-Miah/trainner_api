from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.schemas.auth.reset_password import ResetPasswordRequest
from src.service.auth.reset_password import reset_password


router = APIRouter(
    prefix=settings.reset_password_prefix,
    tags=["Reset Password"],
)


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
async def reset_password_account(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    result = await reset_password(
        db=db,
        request=request,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="Password reset successfully.",
        data=result,
    )