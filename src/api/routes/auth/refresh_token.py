from fastapi import APIRouter, status
from src.core.config import settings
from src.schemas.auth.refresh_token import RefreshTokenRequest
from src.core.common_responses import CommonResponse
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
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh the access token using a valid refresh token.
    """
    # Here you would typically validate the refresh token and generate a new access token.
    # For demonstration purposes, we'll just return a dummy response.

    # In a real implementation, you would check if the refresh token is valid,
    # and if so, generate a new access token and return it.
    refresh_response = await refresh_access_token(request.refresh_token)

    return CommonResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="Access token refreshed successfully.",
        data=refresh_response
    )