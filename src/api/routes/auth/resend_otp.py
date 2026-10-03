from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.schemas.auth.email_verify import ResendOTPRequest
from src.service.auth.resend_otp import resend_otp


router = APIRouter(
    prefix=settings.resend_otp_prefix,
    tags=["Resend OTP"],
)


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
async def resend_otp_account(
    request: ResendOTPRequest,
    db: Session = Depends(get_db),
):
    result = await resend_otp(
        db=db,
        user_id=request.user_id,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="A new OTP has been sent to your email.",
        data=result,
    )