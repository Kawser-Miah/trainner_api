from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.schemas.auth.verify_reset_code import (
    VerifyResetCodeRequest,
    VerifyResetCodeResponse,
)
from src.service.auth.verify_reset_code import verify_reset_code


router = APIRouter(
    prefix=settings.verify_reset_code_prefix,
    tags=["Verify Reset Code"],
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
    include_in_schema=False,
)
async def verify_reset_code_account(
    request: VerifyResetCodeRequest,
    db: Session = Depends(get_db),
):
    result = await verify_reset_code(
        db=db,
        user_id=request.user_id,
        code=request.code,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        status=status.HTTP_200_OK,
        message="Code verified successfully",
        data=VerifyResetCodeResponse(**result),
    )
