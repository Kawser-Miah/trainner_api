from typing import Any
from pydantic import BaseModel


class CommonResponse(BaseModel):
    success: bool
    status: int | None = None
    message: str
    data: Any | None = None

    def __init__(self, **data: Any):
        if "code" in data and "status" not in data:
            data["status"] = data.pop("code")
        elif "code" in data:
            data.pop("code")
        if "status" not in data:
            data["status"] = 200
        super().__init__(**data)


class ErrorResponse(BaseModel):
    success: bool = False
    status: int | None = None
    message: str
    error: Any | None = None
    data: Any | None = None

    def __init__(self, **data: Any):
        if "code" in data and "status" not in data:
            data["status"] = data.pop("code")
        elif "code" in data:
            data.pop("code")
        if "status" not in data:
            data["status"] = 400
        super().__init__(**data)
