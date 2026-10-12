from pydantic import BaseModel, ConfigDict

from src.schemas.client.browse.service_schemas import ClientServiceProviderDetails


class UserBlogCategoryDetails(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserBlogItemResponse(BaseModel):
    id: int
    coach: ClientServiceProviderDetails
    category: int
    category_details: UserBlogCategoryDetails | None = None
    title: str
    content: str
    image: str | None = None
    status: str = "published"
    read_time_minutes: int = 1
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
