from fastapi import APIRouter, status

from src.core.config import settings
from src.core.common_responses import CommonResponse
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
):
    result = await resend_otp(
        user_id=request.user_id,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="A new OTP has been sent to your email.",
        data=result,
    )