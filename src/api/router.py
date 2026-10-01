from fastapi import APIRouter
from src.core.config import settings
from src.api.routes.auth import register_account

from pydantic import BaseModel

api_router = APIRouter()
api_router.include_router(register_account.router, prefix=settings.authentication_prefix)
