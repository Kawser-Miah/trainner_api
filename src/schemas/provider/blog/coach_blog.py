from pydantic import BaseModel, ConfigDict, Field


class CoachBlogCategoryDetailsResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CreateCoachBlogRequest(BaseModel):
    title: str
    category: int = Field(..., description="Category ID")
    content: str
    status: str = "published"


class UpdateCoachBlogRequest(BaseModel):
    title: str | None = None
    category: int | None = None
    content: str | None = None
    status: str | None = None


class CoachBlogDataResponse(BaseModel):
    id: int
    coach: int
    category: int
    category_details: CoachBlogCategoryDetailsResponse | None = None
    title: str
    content: str
    image: str | None = None
    status: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class DeleteCoachBlogDataResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)
