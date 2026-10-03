from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.schemas.auth.sign_in import SignInRequest
from src.service.auth.sign_in import sign_in


router = APIRouter(
    prefix=settings.sign_in_prefix,
    tags=["Sign In"],
)


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponse,
)
async def sign_in_account(
    request: SignInRequest,
    db: Session = Depends(get_db),
):
    result = await sign_in(
        db=db,
        email=str(request.email),
        password=request.password,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="Sign in successful.",
        data=result,
    )