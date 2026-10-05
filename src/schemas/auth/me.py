from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: str | None = None
    address: str | None = None
    image: str | None = None
    role: str
    is_verified: bool
    is_completed: bool
    coach_status: str | None = None
    created_at: datetime | str

    model_config = ConfigDict(from_attributes=True)
