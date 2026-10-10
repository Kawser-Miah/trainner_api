from typing import Any
from pydantic import BaseModel


class CommonResponse(BaseModel):
    success: bool
    code: int | None = None
    status: int | None = None
    message: str
    data: Any | None = None

    def __init__(self, **data: Any):
        if "code" in data and "status" not in data:
            data["status"] = data["code"]
        elif "status" in data and "code" not in data:
            data["code"] = data["status"]
        elif "code" not in data and "status" not in data:
            data["code"] = 200
            data["status"] = 200
        super().__init__(**data)


class ErrorResponse(BaseModel):
    success: bool = False
    code: int | None = None
    status: int | None = None
    message: str
    error: Any | None = None
    data: Any | None = None

    def __init__(self, **data: Any):
        if "code" in data and "status" not in data:
            data["status"] = data["code"]
        elif "status" in data and "code" not in data:
            data["code"] = data["status"]
        super().__init__(**data)
