from pydantic import BaseModel, Field


class DeleteAccountRequest(BaseModel):
    password: str = Field(..., min_length=1, description="Account password to confirm deletion")


class DeleteAccountResponse(BaseModel):
    success: bool = True
    status: int = 200
    message: str = "Your account has been deleted."
