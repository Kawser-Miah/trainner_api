from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.schemas.auth.account import RegisterAccountRequest
from src.service.auth.register import register_user


router = APIRouter(
    prefix=settings.register_account_prefix,
    tags=["Register Account"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommonResponse,
)
async def register_account(
    request: RegisterAccountRequest,
    db: Session = Depends(get_db),
):
    user = await register_user(
        db=db,
        register_account_request=request,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_201_CREATED,
        message="Registration completed successfully. OTP sent to your email for verification.",
        data={
            "user_id": str(user.id),
        },
    )