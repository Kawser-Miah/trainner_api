from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.accounts.user import User
from src.schemas.auth.delete_account import (
    DeleteAccountRequest,
    DeleteAccountResponse,
)
from src.service.auth.delete_account import delete_user_account


router = APIRouter(
    prefix=settings.delete_account_prefix,
    tags=["Delete Account"],
)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=DeleteAccountResponse,
    response_model_exclude_none=True,
    summary="Delete Account",
    description="Deletes the authenticated user's account after verifying their password.",
)
@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=DeleteAccountResponse,
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def delete_account(
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await delete_user_account(
        db=db,
        user=current_user,
        password=request.password,
    )

    return DeleteAccountResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Your account has been deleted.",
    )
