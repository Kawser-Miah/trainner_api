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


from src.api.routes.provider.coach_profile import (
    coach_availability,
    coach_profile,
    coach_reviews,
)
from src.api.routes.provider.blog import coach_blog
from src.api.routes.provider.service import coach_service
from src.api.routes.provider.product import coach_product
from src.api.routes.provider.category import coach_category
from src.api.routes.client.browse import (
    user_category_list_router,
    coach_profile_list_router,
    recommended_coach_profile_list_router,
    coach_profile_detail_router,
    coach_availability_date_router,
    coach_availability_month_router,
    coach_reviews_router,
    user_service_list_router,
    user_service_detail_router,
    digital_product_list_router,
    digital_product_detail_router,
    digital_product_download_router,
    user_blog_list_router,
    user_blog_detail_router,
    app_rating_router,
)
from src.api.routes.client.booking_and_payments import (
    book_service_router,
    product_purchase_router,
    stripe_checkout_router,
)


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
api_router.include_router(coach_profile.router, prefix=settings.provider_prefix)
api_router.include_router(coach_profile.router, prefix=settings.provider_prefix.lower(), include_in_schema=False)
api_router.include_router(coach_availability.router, prefix=settings.provider_prefix)
api_router.include_router(coach_availability.router, prefix=settings.provider_prefix.lower(), include_in_schema=False)
api_router.include_router(coach_reviews.router, prefix=settings.provider_prefix)
api_router.include_router(coach_reviews.router, prefix=settings.provider_prefix.lower(), include_in_schema=False)
api_router.include_router(coach_service.router, prefix=settings.provider_prefix)
api_router.include_router(coach_service.router, prefix=settings.provider_prefix.lower(), include_in_schema=False)
api_router.include_router(coach_blog.router, prefix=settings.provider_prefix)
api_router.include_router(coach_blog.router, prefix=settings.provider_prefix.lower(), include_in_schema=False)
api_router.include_router(coach_product.router, prefix=settings.provider_prefix)
api_router.include_router(coach_product.router, prefix=settings.provider_prefix.lower(), include_in_schema=False)
api_router.include_router(coach_category.router, prefix=settings.provider_prefix)
api_router.include_router(coach_category.router, prefix=settings.provider_prefix.lower(), include_in_schema=False)
api_router.include_router(coach_product.download_router)

# Client Browse endpoints (/user)
api_router.include_router(user_category_list_router, prefix=settings.client_prefix)
api_router.include_router(coach_profile_list_router, prefix=settings.client_prefix)
api_router.include_router(recommended_coach_profile_list_router, prefix=settings.client_prefix)
api_router.include_router(coach_profile_detail_router, prefix=settings.client_prefix)
api_router.include_router(coach_availability_date_router, prefix=settings.client_prefix)
api_router.include_router(coach_availability_month_router, prefix=settings.client_prefix)
api_router.include_router(coach_reviews_router, prefix=settings.client_prefix)
api_router.include_router(user_service_list_router, prefix=settings.client_prefix)
api_router.include_router(user_service_detail_router, prefix=settings.client_prefix)
api_router.include_router(digital_product_list_router, prefix=settings.client_prefix)
api_router.include_router(digital_product_detail_router, prefix=settings.client_prefix)
api_router.include_router(digital_product_download_router, prefix=settings.client_prefix)
api_router.include_router(user_blog_list_router, prefix=settings.client_prefix)
api_router.include_router(user_blog_detail_router, prefix=settings.client_prefix)
api_router.include_router(app_rating_router, prefix=settings.client_prefix)

# Client Booking & Payments endpoints (/payments)
api_router.include_router(book_service_router, prefix=settings.payments_prefix)
api_router.include_router(book_service_router, prefix=f"{settings.client_prefix}{settings.payments_prefix}", include_in_schema=False)
api_router.include_router(product_purchase_router, prefix=settings.payments_prefix)
api_router.include_router(product_purchase_router, prefix=f"{settings.client_prefix}{settings.payments_prefix}", include_in_schema=False)
api_router.include_router(stripe_checkout_router, prefix=settings.payments_prefix)
api_router.include_router(stripe_checkout_router, prefix=f"{settings.client_prefix}{settings.payments_prefix}", include_in_schema=False)




