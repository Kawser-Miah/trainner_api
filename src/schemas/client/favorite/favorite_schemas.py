from pydantic import BaseModel, ConfigDict

from src.schemas.client.browse.coach_schemas import CoachProfileListItemResponse


class CoachFavoriteToggleResponseData(BaseModel):
    coach_id: int
    is_favorited: bool

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "CoachFavoriteToggleResponseData",
    "CoachProfileListItemResponse",
]
