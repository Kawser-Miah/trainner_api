from typing import Any
from pydantic import BaseModel


class CommonResponse(BaseModel):
    success: bool
    code: int
    message: str
    data: Any | None = None

class ErrorResponse(BaseModel):
    success: bool = False
    code: int
    message: str
    error: Any | None = None