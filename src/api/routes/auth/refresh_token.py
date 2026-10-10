from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.common_responses import CommonResponse
from src.core.config import settings
from src.core.database import get_db
from src.schemas.auth.refresh_token import RefreshTokenRequest
from src.service.auth.refresh_token import refresh_access_token

router = APIRouter(
    prefix=settings.refresh_token_prefix,
    tags=["Refresh Token"],
)

@router.post(
    "/",
    response_model=CommonResponse,
    status_code=status.HTTP_200_OK
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh the access token using a valid refresh token.
    """
    refresh_response = await refresh_access_token(
        db=db,
        refresh_token=request.refresh_token,
    )

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="Access token refreshed successfully.",
        data=refresh_response
    )