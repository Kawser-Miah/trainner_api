from fastapi import APIRouter, status
from src.core.config import settings
from src.schemas.auth.account import RegisterAccountRequest, RegisterAccountResponse
from src.core.common_responses import CommonResponse
from src.service.auth.register import register_user

router = APIRouter(
    prefix=settings.register_account_prefix,
    tags=["Register Account"]
)

@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=CommonResponse,)
async def register_account(request: RegisterAccountRequest):
    user = await register_user(request)

    return CommonResponse(
        success=True,
        code=status.HTTP_201_CREATED,
        message="Registration completed successfully. OTP sent to your email for verification.",
        data={
            "user_id": user["id"],
        },
    )