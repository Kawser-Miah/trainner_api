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
    delete_account_prefix: str = "/delete-account"
    provider_prefix: str = "/Provider"
    client_prefix: str = "/user"
    coach_profile_prefix: str = "/coach-profile"
    coach_availability_prefix: str = "/coach-availability"
    coach_reviews_prefix: str = "/reviews"
    coach_services_prefix: str = "/services"
    service_create_prefix: str = "/create"
    service_list_prefix: str = "/list"
    coach_blogs_prefix: str = "/blogs"
    blog_create_prefix: str = "/create"
    blog_list_prefix: str = "/list"
    coach_products_prefix: str = "/products"
    product_create_prefix: str = "/create"
    product_list_prefix: str = "/products-list"
    category_list_prefix: str = "/categories-list"
    user_category_list_prefix: str = "/user-category-list"
    coach_profile_list_prefix: str = "/coach-profile-list"
    recommended_coach_profile_list_prefix: str = "/recommended-coach-profile-list"
    client_coach_profile_detail_prefix: str = "/coach-profile"
    client_coaches_prefix: str = "/coaches"
    client_availability_prefix: str = "/availability"
    client_reviews_prefix: str = "/reviews"
    user_service_list_prefix: str = "/user-service-list"
    user_service_detail_prefix: str = "/user-service-detail"
    digital_product_list_prefix: str = "/digital-product-list"
    digital_product_detail_prefix: str = "/digital-product-detail"
    digital_product_download_prefix: str = "/digital-product-download"
    user_blog_list_prefix: str = "/blog-list"
    user_blog_detail_prefix: str = "/blog-detail"
    app_rating_prefix: str = "/app-rating"
    app_ratings_list_prefix: str = "/app-ratings-list"
    payments_prefix: str = "/payments"
    book_service_prefix: str = "/book-service"
    product_purchase_prefix: str = "/products/purchase"
    stripe_prefix: str = "/stripe"
    create_checkout_session_prefix: str = "/create-checkout-session"
    stripe_webhook_prefix: str = "/webhook"
    client_fee_percentage: float = 3.00
    coach_fee_percentage: float = 5.00
    booking_payment_timeout_minutes: int = 15
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""



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