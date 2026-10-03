from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.schemas.auth.email_verify import VerifyEmailRequest
from src.service.auth.email_verification import verify_email


router = APIRouter(
    prefix=settings.verify_email_prefix,
    tags=["Verify Email"],
)


@router.post(
    "/",
    summary="Verify Email",
    description="Verify the user's email with the provided OTP.",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
async def verify_email_account(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    result = await verify_email(
        db=db,
        user_id=request.user_id,
        code=request.code,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="Email Verification Successfully!",
        data=result,
    )