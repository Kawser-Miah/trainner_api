from pydantic import BaseModel, ConfigDict, Field
from src.core.common_responses import CommonResponse


class CoachReviewItemResponse(BaseModel):
    id: int
    user_name: str
    user_image: str | None = None
    rating: int
    review: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class CoachReviewsDataResponse(BaseModel):
    avg_rating: float = 0.0
    total_reviews: int = 0
    rating_breakdown: dict[str, int] = Field(
        default_factory=lambda: {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    )
    reviews: list[CoachReviewItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


CoachReviewsResponse = CommonResponse
