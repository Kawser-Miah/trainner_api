from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.schemas.auth.forgot_password import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
)
from src.service.auth.forgot_password import forgot_password


router = APIRouter(
    prefix=settings.forgot_password_prefix,
    tags=["Forgot Password"],
)


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
async def forgot_password_account(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    result = await forgot_password(
        db=db,
        email=str(request.email),
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="Reset password code sent successfully. Please check your email!",
        data=ForgotPasswordResponse(**result),
    )