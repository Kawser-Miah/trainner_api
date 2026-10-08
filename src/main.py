"""FastAPI application entry point.

Coach Hub - Book Coaches for Sessions and Events
Provides a platform for users to find and connect with coaches in various fields, including sports, fitness, personal development, and more.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from src.core.config import settings
from src.api import router
from src.core.exceptions import AppException
from src.core.common_responses import ErrorResponse



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("=" * 60)
    print(f"🚀 {settings.app_name} v{settings.version}")
    print("=" * 60)
    # print(f"📊 Model loaded from: {settings.model_path}")
    # print(f"📐 Scaler loaded from: {settings.scaler_path}")
    print(f"📝 Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down API...")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    return JSONResponse(
        status_code=exc.status,
        content=ErrorResponse(
            code=exc.status,
            message=exc.message,
            error=exc.error,
        ).model_dump(),
    )

# Configure CORS (Cross-Origin Resource Sharing)
# Allows Flutter app to make requests to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static media files
media_dir = Path("media")
media_dir.mkdir(parents=True, exist_ok=True)
(media_dir / "profile_images").mkdir(parents=True, exist_ok=True)
(media_dir / "coach" / "profile").mkdir(parents=True, exist_ok=True)
(media_dir / "coach" / "videos" / "thumbnails").mkdir(parents=True, exist_ok=True)
(media_dir / "coach" / "certificates").mkdir(parents=True, exist_ok=True)
(media_dir / "coach" / "qualifications").mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

# Include API routers
app.include_router(
    router.api_router,
    prefix=settings.api_prefix,
)

# app.include_router(
#     ai_chat.router,
#     tags=["AI Chat"]
# )

# app.include_router(
#     smart_irrigation.router,
#     tags=["Smart Irrigation"]
# )

# app.include_router(
#     fertilizer_tips.router,
#     tags=["Fertilizer Tips"]
# )

# app.include_router(
#     yield_estimation.router,
#     tags=["Yield Estimation"]
# )

# app.include_router(
#     crop_recommendation.router,
#     tags=["Crop Recommendation"]
# )

# app.include_router(
#     price_predection.router,
#     tags=["Price Prediction"]
# )



@app.get(
    "/",
    tags=["Root"],
    summary="API information",
    description="Get API metadata and available endpoints."
)
async def root():
    """Root endpoint - returns API information."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "description": settings.description,
        "endpoints": {
            "root": f"{settings.api_prefix}/",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "status": "running"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running and healthy."
)
async def health_check():
    """Health check endpoint - verifies API is operational."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version
    }