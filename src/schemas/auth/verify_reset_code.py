from pydantic import BaseModel, Field


class VerifyResetCodeRequest(BaseModel):
    user_id: str | int = Field(..., description="User ID")
    code: str = Field(..., min_length=4, max_length=10, description="OTP reset code")


class VerifyResetCodeResponse(BaseModel):
    secret_key: str
    user_id: str
