from fastapi import APIRouter
from src.core.config import settings


router = APIRouter(
    prefix=settings.verify_email_prefix,
    tags=["Verify Email"]
)

@router.post("/",
             status_code=200)
async def verify_otp():
    return {"message": "OTP verification endpoint"}