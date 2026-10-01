from fastapi import APIRouter, status
from src.core.config import settings
from src.schemas.auth.email_verify import  VerifyEmailRequest, VerifyEmailResponse
from src.core.common_responses import CommonResponse
from src.service.auth.email_verification import verify_email


router = APIRouter(
    prefix=settings.verify_email_prefix,
    tags=["Verify Email"]
)

@router.post("/",
             summary="Verify Email",
             description="Verify the user's email with the provided OTP.",
             status_code=status.HTTP_200_OK,
             response_model=VerifyEmailResponse,)
@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
async def verify_email_account(
    request: VerifyEmailRequest,
):
    result = await verify_email(
        user_id=request.user_id,
        code=request.code,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="Email Verification Successfully!",
        data=result,
    )