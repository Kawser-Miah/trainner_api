from src.api.routes.provider.coach_profile.coach_availability import (
    router as availability_router,
)
from src.api.routes.provider.coach_profile.coach_profile import (
    router as coach_profile_router,
)
from src.api.routes.provider.coach_profile.coach_profile import router
from src.api.routes.provider.coach_profile.coach_reviews import (
    router as coach_reviews_router,
)

__all__ = ["router", "coach_profile_router", "availability_router", "coach_reviews_router"]
