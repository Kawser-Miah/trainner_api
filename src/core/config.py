"""Application configuration settings.

Manages paths, constants, and environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings and configuration.
    
    Can be overridden by environment variables.
    """
    
    # API Metadata
    app_name: str = "Coach Hub"
    version: str = "1.0.0"
    description: str = "Coach Hub is an commnity driven project to book coach for sessions and events. It provides a platform for users to find and connect with coaches in various fields, including sports, fitness, personal development, and more. The application allows users to browse coach profiles, read reviews, and book sessions directly through the platform."
    
    # Path Configuration
    # base_dir: Path = Path(__file__).parent.parent.parent
    # crop_disease_detection_model_path: Path = base_dir / "assets" / "crop_disease_detection_ml_model.h5"
    # crop_disease_detection_class_names_path: Path = base_dir / "assets" / "crop_disease_detection_class_names.json"
    # smart_irrigation_model_path: Path = base_dir / "assets" / "best_irrigation_model.pkl"
    # irrigation_soil_encoder_path: Path = base_dir / "assets" / "le_soil.pkl"
    # irrigation_crop_encoder_path: Path = base_dir / "assets" / "le_crop.pkl"
    # irrigation_stage_encoder_path: Path = base_dir / "assets" / "le_stage.pkl"
    # fertilizer_model_path: Path = base_dir / "assets" / "fertilizer_model.pkl"
    # fertilizer_encoder_path: Path = base_dir / "assets" / "fertilizer_encoder.pkl"
    # crop_encoder_path: Path = base_dir / "assets" / "crop_encoder.pkl"
    # soil_encoder_path: Path = base_dir / "assets" / "soil_encoder.pkl"
    # yield_model_path: Path = base_dir / "assets" / "yield_model.pkl"
    # item_encoder_path: Path = base_dir / "assets" / "item_encoder.pkl"
    # area_encoder_path: Path = base_dir / "assets" / "area_encoder.pkl"
    # crop_recommendation_model_path: Path = base_dir / "assets" / "crop_recommendation_model.pkl"
    # price_predection_bundle_path: Path = base_dir / "assets" / "price_predection.pkl"

    
    

    
    # API Configuration
    api_prefix: str = "/api"
    authentication_prefix: str = "/auth"
    register_account_prefix: str = "/register"
    verify_email_prefix: str = "/verify-email"
    resend_otp_prefix: str = "/resend-verification-code"
    refresh_token_prefix: str = "/refresh-token"
    sign_in_prefix: str = "/signin"
    reset_password_prefix: str = "/reset-password"
    forgot_password_prefix: str = "/forgot-password"
    change_password_prefix: str = "/change-password"
    verify_reset_code_prefix: str = "/verify-reset-code"
    me_prefix: str = "/me"
    logout_prefix: str = "/logout"




    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = ["*"]  # Change in production
    
    # Supabase Configuration
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""
    google_api_key: str = ""
    DATABASE_URL: str = ""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


# Singleton instance
settings = Settings()