from fastapi import APIRouter
from src.core.config import settings
from src.api.routes.auth import (
    register_account,
    verify_otp,
    resend_otp,
    refresh_token,
    sign_in,
    reset_password,
    forgot_password,
    change_password,
    verify_reset_code,
    me,
    logout,
    delete_account,
)


from src.api.routes.provider.coach_profile import router as provider_coach_profile_router


api_router = APIRouter()
api_router.include_router(register_account.router, prefix=settings.authentication_prefix)
api_router.include_router(verify_otp.router, prefix=settings.authentication_prefix)
api_router.include_router(resend_otp.router, prefix=settings.authentication_prefix)
api_router.include_router(refresh_token.router, prefix=settings.authentication_prefix)
api_router.include_router(sign_in.router, prefix=settings.authentication_prefix)
api_router.include_router(reset_password.router, prefix=settings.authentication_prefix)
api_router.include_router(forgot_password.router, prefix=settings.authentication_prefix)
api_router.include_router(change_password.router, prefix=settings.authentication_prefix)
api_router.include_router(verify_reset_code.router, prefix=settings.authentication_prefix)
api_router.include_router(me.router, prefix=settings.authentication_prefix)
api_router.include_router(logout.router, prefix=settings.authentication_prefix)
api_router.include_router(delete_account.router, prefix=settings.authentication_prefix)

# Provider endpoints
api_router.include_router(provider_coach_profile_router, prefix=settings.provider_prefix)
api_router.include_router(provider_coach_profile_router, prefix=settings.provider_prefix.lower(), include_in_schema=False)
