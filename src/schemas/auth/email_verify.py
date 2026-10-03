from pydantic import BaseModel, Field


class VerifyEmailRequest(BaseModel):
    user_id: str = Field(..., pattern=r"^\d+$")
    code: str


class VerifyEmailResponse(BaseModel):
    access_token: str
    access_token_valid_till: int
    refresh_token: str
    user_id: str
    role: str
    is_completed: bool
    coach_status: str | None

class ResendOTPRequest(BaseModel):
    user_id: str = Field(..., pattern=r"^\d+$")

