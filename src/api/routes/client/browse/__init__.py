from src.api.routes.client.browse.user_category_list import router as user_category_list_router
from src.api.routes.client.browse.coach_profile_list import router as coach_profile_list_router
from src.api.routes.client.browse.recommended_coach_profile_list import (
    router as recommended_coach_profile_list_router,
)
from src.api.routes.client.browse.coach_profile_detail import router as coach_profile_detail_router
from src.api.routes.client.browse.coach_availability_date import (
    router as coach_availability_date_router,
)
from src.api.routes.client.browse.coach_availability_month import (
    router as coach_availability_month_router,
)
from src.api.routes.client.browse.coach_availability import router as coach_availability_router
from src.api.routes.client.browse.coach_reviews import router as coach_reviews_router
from src.api.routes.client.browse.user_service_list import router as user_service_list_router
from src.api.routes.client.browse.user_service_detail import router as user_service_detail_router

__all__ = [
    "user_category_list_router",
    "coach_profile_list_router",
    "recommended_coach_profile_list_router",
    "coach_profile_detail_router",
    "coach_availability_date_router",
    "coach_availability_month_router",
    "coach_availability_router",
    "coach_reviews_router",
    "user_service_list_router",
    "user_service_detail_router",
]
