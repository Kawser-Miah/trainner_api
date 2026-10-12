from pydantic import BaseModel, ConfigDict


class UserCategoryItemResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool = True
    image: str | None = None

    model_config = ConfigDict(from_attributes=True)
