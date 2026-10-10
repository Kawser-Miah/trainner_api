from src.api.routes.provider.coach_profile.coach_availability import (
    router as availability_router,
)
from src.api.routes.provider.coach_profile.coach_profile import (
    router as coach_profile_router,
)
from src.api.routes.provider.coach_profile.coach_profile import router

__all__ = ["router", "coach_profile_router", "availability_router"]
