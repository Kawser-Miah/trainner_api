from pydantic import BaseModel, ConfigDict, Field


class AppRatingCreateRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    review: str = Field(default="", description="Review text")

    model_config = ConfigDict(extra="ignore")


class AppRatingStatsResponse(BaseModel):
    average_rating: float | int = 0
    total_ratings: int = 0
    has_rated: bool = False
    user_rating: int | float | None = None


class AppRatingItemResponse(BaseModel):
    id: int
    user: int
    user_name: str
    rating: int
    review: str
    created_at: str
    updated_at: str


class AppRatingListItemResponse(BaseModel):
    id: int
    user: int
    user_name: str
    image: str | None = None
    rating: int
    review: str
    created_at: str
    updated_at: str
