from fastapi import APIRouter
from src.core.config import settings
from src.api.routes.auth import register_account, verify_otp, resend_otp, refresh_token

from pydantic import BaseModel

api_router = APIRouter()
api_router.include_router(register_account.router, prefix=settings.authentication_prefix)
api_router.include_router(verify_otp.router, prefix=settings.authentication_prefix)
api_router.include_router(resend_otp.router, prefix=settings.authentication_prefix)
api_router.include_router(refresh_token.router, prefix=settings.authentication_prefix)
