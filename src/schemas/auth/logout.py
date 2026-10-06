from pydantic import BaseModel, Field, model_validator


class LogoutRequest(BaseModel):
    refresh: str = Field(..., description="Refresh token to logout")

    @model_validator(mode="before")
    @classmethod
    def populate_refresh(cls, values):
        if isinstance(values, dict):
            if "refresh" not in values and "refresh_token" in values:
                values["refresh"] = values["refresh_token"]
        return values


class LogoutResponse(BaseModel):
    success: bool = True
    status: int = 200
    message: str = "Logged out successfully."
