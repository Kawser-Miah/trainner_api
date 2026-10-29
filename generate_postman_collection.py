import json
import uuid
from pathlib import Path

from src.core.config import settings


def build_url_dict(sub_path: str):
    full_path_str = f"{settings.api_prefix}{sub_path}"
    path_segments = [seg for seg in full_path_str.split("/") if seg]
    return {
        "raw": f"{{{{base_url}}}}{full_path_str}",
        "host": ["{{base_url}}"],
        "path": path_segments,
    }


def make_response_example(name: str, status_code: int, body_dict: dict):
    return [
        {
            "name": name,
            "originalRequest": {},
            "status": "OK" if status_code == 200 or status_code == 201 else "Error",
            "code": status_code,
            "_postman_previewlanguage": "json",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "cookie": [],
            "body": json.dumps(body_dict, indent=2),
        }
    ]


def build_postman_collection():
    collection_id = str(uuid.uuid4())

    auth_prefix = settings.authentication_prefix
    register_url = build_url_dict(f"{auth_prefix}{settings.register_account_prefix}")
    verify_email_url = build_url_dict(f"{auth_prefix}{settings.verify_email_prefix}")
    resend_otp_url = build_url_dict(f"{auth_prefix}{settings.resend_otp_prefix}")
    sign_in_url = build_url_dict(f"{auth_prefix}{settings.sign_in_prefix}")
    refresh_token_url = build_url_dict(f"{auth_prefix}{settings.refresh_token_prefix}")
    me_url = build_url_dict(f"{auth_prefix}{settings.me_prefix}")
    change_password_url = build_url_dict(f"{auth_prefix}{settings.change_password_prefix}")
    forgot_password_url = build_url_dict(f"{auth_prefix}{settings.forgot_password_prefix}")
    verify_reset_code_url = build_url_dict(f"{auth_prefix}{settings.verify_reset_code_prefix}")
    reset_password_url = build_url_dict(f"{auth_prefix}{settings.reset_password_prefix}")
    logout_url = build_url_dict(f"{auth_prefix}{settings.logout_prefix}")
    delete_account_url = build_url_dict(f"{auth_prefix}{settings.delete_account_prefix}")

    provider_profile_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_profile_prefix}")
    provider_categories_list_url = {
        "raw": f"{{{{base_url}}}}{settings.provider_prefix.lstrip('/')}{settings.category_list_prefix}/",
        "host": ["{{base_url}}"],
        "path": [settings.provider_prefix.strip("/"), settings.category_list_prefix.strip("/")],
    }
    provider_availability_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_availability_prefix}")
    provider_reviews_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_reviews_prefix}")
    provider_services_create_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_services_prefix}{settings.service_create_prefix}")
    provider_services_list_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_services_prefix}{settings.service_list_prefix}")
    provider_services_detail_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_services_prefix}/{{{{service_id}}}}")
    provider_services_delete_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_services_prefix}/{{{{service_to_delete_id}}}}")

    provider_blogs_create_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_blogs_prefix}{settings.blog_create_prefix}")
    blogs_list_full_path = f"{settings.api_prefix}{settings.provider_prefix}{settings.coach_blogs_prefix}{settings.blog_create_prefix}"
    blogs_list_segments = [seg for seg in blogs_list_full_path.split("/") if seg]
    provider_blogs_list_url = {
        "raw": f"{{{{base_url}}}}{blogs_list_full_path}?status=published",
        "host": ["{{base_url}}"],
        "path": blogs_list_segments,
        "query": [
            {
                "key": "status",
                "value": "published",
                "description": "Filter blogs by status",
            }
        ],
    }
    provider_blogs_detail_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_blogs_prefix}/{{{{blog_id}}}}")
    provider_blogs_delete_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_blogs_prefix}/{{{{blog_to_delete_id}}}}")

    provider_products_create_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_products_prefix}{settings.product_create_prefix}")
    provider_products_list_url = build_url_dict(f"{settings.provider_prefix}{settings.product_list_prefix}")
    provider_products_detail_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_products_prefix}/{{{{product_id}}}}")
    provider_products_update_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_products_prefix}/{{{{product_id}}}}")
    provider_products_delete_url = build_url_dict(f"{settings.provider_prefix}{settings.coach_products_prefix}/{{{{product_to_delete_id}}}}")

    # Client Browse URLs
    c_prefix = settings.client_prefix.lstrip("/")
    client_category_list_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.user_category_list_prefix}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.user_category_list_prefix.strip("/")],
    }
    client_coach_profile_list_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.coach_profile_list_prefix}?search=&category=&ordering=rating",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.coach_profile_list_prefix.strip("/")],
        "query": [
            {"key": "search", "value": ""},
            {"key": "category", "value": ""},
            {"key": "ordering", "value": "rating"},
        ],
    }
    client_recommended_coaches_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.recommended_coach_profile_list_prefix}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.recommended_coach_profile_list_prefix.strip("/")],
    }
    client_coach_detail_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.client_coach_profile_detail_prefix}/{{{{coach_profile_id}}}}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.client_coach_profile_detail_prefix.strip("/"), "{{coach_profile_id}}"],
    }
    client_coach_avail_date_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.client_coaches_prefix}/{{{{coach_profile_id}}}}{settings.client_availability_prefix}?date={{{{next_monday}}}}&service_id={{{{service_id}}}}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.client_coaches_prefix.strip("/"), "{{coach_profile_id}}", settings.client_availability_prefix.strip("/")],
        "query": [
            {"key": "date", "value": "{{next_monday}}"},
            {"key": "service_id", "value": "{{service_id}}"},
        ],
    }
    client_coach_avail_month_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.client_coaches_prefix}/{{{{coach_profile_id}}}}{settings.client_availability_prefix}?month={{{{month}}}}&service_id={{{{service_id}}}}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.client_coaches_prefix.strip("/"), "{{coach_profile_id}}", settings.client_availability_prefix.strip("/")],
        "query": [
            {"key": "month", "value": "{{month}}"},
            {"key": "service_id", "value": "{{service_id}}"},
        ],
    }
    client_coach_reviews_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.client_coaches_prefix}/{{{{coach_profile_id}}}}{settings.client_reviews_prefix}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.client_coaches_prefix.strip("/"), "{{coach_profile_id}}", settings.client_reviews_prefix.strip("/")],
    }
    client_service_list_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.user_service_list_prefix}?search=&coach_profile={{{{coach_profile_id}}}}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.user_service_list_prefix.strip("/")],
        "query": [
            {"key": "search", "value": ""},
            {"key": "coach_profile", "value": "{{coach_profile_id}}"},
        ],
    }
    client_service_detail_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.user_service_detail_prefix}/{{{{service_id}}}}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.user_service_detail_prefix.strip("/"), "{{service_id}}"],
    }
    client_digital_product_list_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.digital_product_list_prefix}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.digital_product_list_prefix.strip("/")],
    }
    client_digital_product_detail_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.digital_product_detail_prefix}/{{{{product_id}}}}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.digital_product_detail_prefix.strip("/"), "{{product_id}}"],
    }
    client_digital_product_download_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.digital_product_download_prefix}/{{{{product_id}}}}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.digital_product_download_prefix.strip("/"), "{{product_id}}"],
    }
    client_blog_list_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.user_blog_list_prefix}?category=",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.user_blog_list_prefix.strip("/")],
        "query": [
            {"key": "category", "value": ""},
        ],
    }
    client_blog_detail_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.user_blog_detail_prefix}/{{{{blog_id}}}}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.user_blog_detail_prefix.strip("/"), "{{blog_id}}"],
    }
    client_app_rating_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.app_rating_prefix}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.app_rating_prefix.strip("/")],
    }
    client_app_ratings_list_url = {
        "raw": f"{{{{base_url}}}}/{c_prefix}{settings.app_ratings_list_prefix}",
        "host": ["{{base_url}}"],
        "path": [c_prefix, settings.app_ratings_list_prefix.strip("/")],
    }

    # Client Booking & Payments URLs
    client_book_service_url = build_url_dict(f"{settings.payments_prefix}{settings.book_service_prefix}")
    client_stripe_checkout_url = build_url_dict(f"{settings.payments_prefix}{settings.stripe_prefix}{settings.create_checkout_session_prefix}")
    client_stripe_webhook_url = build_url_dict(f"{settings.payments_prefix}{settings.stripe_prefix}{settings.stripe_webhook_prefix}")




    collection = {
        "info": {
            "_postman_id": collection_id,
            "name": "Personal Project",
            "description": "Postman Collection for Coach Hub API Backend mapped 1:1 with Pydantic Schemas and Settings",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "string",
            },
            {
                "key": "access_token",
                "value": "",
                "type": "string",
            },
            {
                "key": "refresh_token",
                "value": "",
                "type": "string",
            },
            {
                "key": "user_id",
                "value": "",
                "type": "string",
            },
            {
                "key": "secret_key",
                "value": "",
                "type": "string",
            },
            {
                "key": "service_id",
                "value": "1",
                "type": "string",
            },
            {
                "key": "category_id",
                "value": "1",
                "type": "string",
            },
            {
                "key": "service_to_delete_id",
                "value": "3",
                "type": "string",
            },
            {
                "key": "blog_id",
                "value": "1",
                "type": "string",
            },
            {
                "key": "blog_to_delete_id",
                "value": "2",
                "type": "string",
            },
            {
                "key": "product_id",
                "value": "1",
                "type": "string",
            },
            {
                "key": "product_to_delete_id",
                "value": "2",
                "type": "string",
            },
            {
                "key": "coach_profile_id",
                "value": "1",
                "type": "string",
            },
            {
                "key": "next_monday",
                "value": "2026-10-12",
                "type": "string",
            },
            {
                "key": "month",
                "value": "2026-10",
                "type": "string",
            },
            {
                "key": "booking_id",
                "value": "1",
                "type": "string",
            },
            {
                "key": "checkout_session_id",
                "value": "cs_test_a1b2c3d4e5f6",
                "type": "string",
            },
            {
                "key": "checkout_url",
                "value": "",
                "type": "string",
            },
            {
                "key": "stripe_signature",
                "value": "test_signature",
                "type": "string",
            },
        ],

        "item": [
            {
                "name": "Authentication",
                "item": [
                    {
                        "name": "Register Account",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "full_name": "Test Coach",
                                        "email": "coach@example.com",
                                        "phone": "+1234567890",
                                        "address": "123 Main Street",
                                        "password": "Password123!",
                                        "confirm_password": "Password123!",
                                        "role": "COACH",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": register_url,
                        },
                        "response": make_response_example(
                            "Register Success Example",
                            201,
                            {
                                "success": True,
                                "status": 201,
                                "message": "Account registered successfully. Please check your email for OTP verification.",
                                "data": {"user_id": "24"},
                            },
                        ),
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData && jsonData.data && jsonData.data.user_id) {",
                                        '    pm.collectionVariables.set("user_id", jsonData.data.user_id);',
                                        "}",
                                    ],
                                    "type": "text/javascript",
                                },
                            }
                        ],
                    },
                    {
                        "name": "Verify Email (OTP)",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "user_id": "{{user_id}}",
                                        "code": "123456",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": verify_email_url,
                        },
                        "response": make_response_example(
                            "Verify Email Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Email verified successfully.",
                                "data": {
                                    "access_token": "eyJhbGciOi...",
                                    "access_token_valid_till": 1775836800000,
                                    "refresh_token": "eyJhbGciOi...",
                                    "user_id": "24",
                                    "role": "COACH",
                                    "is_completed": False,
                                    "coach_status": "pending",
                                },
                            },
                        ),
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData && jsonData.data) {",
                                        "    if (jsonData.data.access_token) {",
                                        '        pm.collectionVariables.set("access_token", jsonData.data.access_token);',
                                        "    }",
                                        "    if (jsonData.data.refresh_token) {",
                                        '        pm.collectionVariables.set("refresh_token", jsonData.data.refresh_token);',
                                        "    }",
                                        "}",
                                    ],
                                    "type": "text/javascript",
                                },
                            }
                        ],
                    },
                    {
                        "name": "Resend Verification Code (OTP)",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "user_id": "{{user_id}}",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": resend_otp_url,
                        },
                        "response": make_response_example(
                            "Resend Code Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Verification code sent successfully.",
                            },
                        ),
                    },
                    {
                        "name": "Sign In",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "email": "coach@example.com",
                                        "password": "Password123!",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": sign_in_url,
                        },
                        "response": make_response_example(
                            "Sign In Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Signed in successfully.",
                                "data": {
                                    "access_token": "eyJhbGciOi...",
                                    "access_token_valid_till": 1775836800000,
                                    "refresh_token": "eyJhbGciOi...",
                                    "user_id": "24",
                                    "role": "COACH",
                                    "is_completed": True,
                                    "coach_status": "approved",
                                },
                            },
                        ),
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData && jsonData.data) {",
                                        "    if (jsonData.data.access_token) {",
                                        '        pm.collectionVariables.set("access_token", jsonData.data.access_token);',
                                        "    }",
                                        "    if (jsonData.data.refresh_token) {",
                                        '        pm.collectionVariables.set("refresh_token", jsonData.data.refresh_token);',
                                        "    }",
                                        "    if (jsonData.data.user_id) {",
                                        '        pm.collectionVariables.set("user_id", jsonData.data.user_id);',
                                        "    }",
                                        "}",
                                    ],
                                    "type": "text/javascript",
                                },
                            }
                        ],
                    },
                    {
                        "name": "Refresh Token",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "refresh_token": "{{refresh_token}}",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": refresh_token_url,
                        },
                        "response": make_response_example(
                            "Refresh Token Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Access token refreshed successfully.",
                                "data": {
                                    "access_token": "eyJhbGciOi...",
                                    "access_token_valid_till": 1775836800000,
                                    "refresh_token": "eyJhbGciOi...",
                                },
                            },
                        ),
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData && jsonData.data && jsonData.data.access_token) {",
                                        '    pm.collectionVariables.set("access_token", jsonData.data.access_token);',
                                        "}",
                                    ],
                                    "type": "text/javascript",
                                },
                            }
                        ],
                    },
                    {
                        "name": "Get Current User Profile (Me)",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": me_url,
                        },
                        "response": make_response_example(
                            "User Profile Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "User profile retrieved successfully.",
                                "data": {
                                    "id": 24,
                                    "email": "coach@example.com",
                                    "full_name": "Test Coach",
                                    "phone_number": "+1234567890",
                                    "address": "123 Main Street",
                                    "image": "http://localhost:8000/media/profile_images/avatar.jpg",
                                    "role": "Coach",
                                    "is_verified": True,
                                    "is_completed": True,
                                    "coach_status": "approved",
                                    "created_at": "2026-10-10T08:00:00Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Update User Profile (Me)",
                        "request": {
                            "method": "PATCH",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {"key": "full_name", "value": "Test Coach Updated", "type": "text"},
                                    {"key": "phone_number", "value": "+1987654321", "type": "text"},
                                    {"key": "address", "value": "456 Updated St", "type": "text"},
                                    {"key": "image", "type": "file", "src": []},
                                ],
                            },
                            "url": me_url,
                        },
                    },
                    {
                        "name": "Change Password",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Authorization", "value": "Bearer {{access_token}}"},
                                {"key": "Content-Type", "value": "application/json"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "old_password": "Password123!",
                                        "new_password": "NewPassword123!",
                                        "re_new_password": "NewPassword123!",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": change_password_url,
                        },
                    },
                    {
                        "name": "Forgot Password",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "email": "coach@example.com",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": forgot_password_url,
                        },
                        "response": make_response_example(
                            "Forgot Password Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Password reset code sent to your email.",
                                "data": {
                                    "user_id": "24",
                                    "expires_at": 1775836800,
                                },
                            },
                        ),
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData && jsonData.data && jsonData.data.user_id) {",
                                        '    pm.collectionVariables.set("user_id", jsonData.data.user_id);',
                                        "}",
                                    ],
                                    "type": "text/javascript",
                                },
                            }
                        ],
                    },
                    {
                        "name": "Verify Reset Code",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "user_id": "{{user_id}}",
                                        "code": "123456",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": verify_reset_code_url,
                        },
                        "response": make_response_example(
                            "Verify Reset Code Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Reset code verified successfully.",
                                "data": {
                                    "secret_key": "SEC_1234567890",
                                    "user_id": "24",
                                },
                            },
                        ),
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData && jsonData.data && jsonData.data.secret_key) {",
                                        '    pm.collectionVariables.set("secret_key", jsonData.data.secret_key);',
                                        "}",
                                    ],
                                    "type": "text/javascript",
                                },
                            }
                        ],
                    },
                    {
                        "name": "Reset Password",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "secret_key": "{{secret_key}}",
                                        "new_password": "NewPassword123!",
                                        "confirm_password": "NewPassword123!",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": reset_password_url,
                        },
                    },
                    {
                        "name": "Logout",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Authorization", "value": "Bearer {{access_token}}"},
                                {"key": "Content-Type", "value": "application/json"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "refresh": "{{refresh_token}}",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": logout_url,
                        },
                    },
                    {
                        "name": "Delete Account",
                        "request": {
                            "method": "DELETE",
                            "header": [
                                {"key": "Authorization", "value": "Bearer {{access_token}}"},
                                {"key": "Content-Type", "value": "application/json"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "password": "Password123!",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": delete_account_url,
                        },
                    },
                ],
            },
            {
                "name": "Provider Coach Profile",
                "item": [
                    {
                        "name": "Get Coach Profile",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": provider_profile_url,
                        },
                        "response": make_response_example(
                            "Get Profile Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Coach profile retrieved successfully.",
                                "data": {
                                    "id": 1,
                                    "user": {
                                        "id": 24,
                                        "full_name": "Test Coach",
                                        "email": "coach@example.com",
                                        "phone_number": "+1234567890",
                                        "address": "123 Main Street",
                                    },
                                    "profile_photo": "http://localhost:8000/media/coach/profile/avatar.jpg",
                                    "headline": "Certified Senior Fitness & Health Coach",
                                    "about": "Passionate about helping clients achieve their peak athletic performance and overall wellbeing.",
                                    "categories": [
                                        {
                                            "id": 1,
                                            "name": "Fitness",
                                            "description": "Fitness and body training",
                                            "is_active": True,
                                            "image": "http://localhost:8000/media/categories/fitness.jpg",
                                        }
                                    ],
                                    "certifications": [
                                        {
                                            "id": 1,
                                            "name": "NASM Certified Personal Trainer",
                                            "document": "http://localhost:8000/media/coach/certificates/nasm_cert.pdf",
                                            "created_at": "2026-10-10T08:00:00Z",
                                        }
                                    ],
                                    "qualifications": [
                                        {
                                            "id": 1,
                                            "name": "B.Sc. Sports Science",
                                            "document": "http://localhost:8000/media/coach/qualifications/degree.pdf",
                                            "created_at": "2026-10-10T08:00:00Z",
                                        }
                                    ],
                                    "introduction_video": "http://localhost:8000/media/coach/videos/intro.mp4",
                                    "introduction_video_duration": 222,
                                    "introduction_video_duration_display": "3:42",
                                    "introduction_video_thumbnail": "http://localhost:8000/media/coach/videos/thumbnails/thumb.jpg",
                                    "linkedin_url": "https://linkedin.com/in/coach-john-doe",
                                    "affiliate_commission_percent": "20.00",
                                    "auto_approve_affiliates": False,
                                    "expertises": ["Fitness", "Nutrition", "HIIT"],
                                    "languages": ["English", "Spanish"],
                                    "is_completed": True,
                                    "status": "approved",
                                    "rejection_reason": "",
                                    "avg_rating": 4.9,
                                    "total_reviews": 15,
                                    "completed_sessions_count": 42,
                                    "success_rate": 98.5,
                                    "created_at": "2026-10-10T08:00:00Z",
                                    "updated_at": "2026-10-10T09:00:00Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Create Coach Profile",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {
                                        "key": "headline",
                                        "value": "Certified Senior Fitness & Health Coach",
                                        "type": "text",
                                    },
                                    {
                                        "key": "about",
                                        "value": "Passionate about helping clients achieve their peak athletic performance and overall wellbeing.",
                                        "type": "text",
                                    },
                                    {
                                        "key": "linkedin_url",
                                        "value": "https://linkedin.com/in/coach-john-doe",
                                        "type": "text",
                                    },
                                    {
                                        "key": "category_ids",
                                        "value": "[1, 2]",
                                        "type": "text",
                                    },
                                    {
                                        "key": "expertises",
                                        "value": "['Fitness', 'Nutrition', 'HIIT']",
                                        "type": "text",
                                    },
                                    {
                                        "key": "languages",
                                        "value": "['English', 'Spanish']",
                                        "type": "text",
                                    },
                                    {
                                        "key": "introvideo",
                                        "type": "file",
                                        "src": [],
                                    },
                                    {
                                        "key": "introduction_video_thumbnail",
                                        "type": "file",
                                        "src": [],
                                    },
                                    {
                                        "key": "certifications[0][name]",
                                        "value": "NASM Certified Personal Trainer",
                                        "type": "text",
                                    },
                                    {
                                        "key": "certifications[0][document]",
                                        "type": "file",
                                        "src": [],
                                    },
                                    {
                                        "key": "qualifications[0][name]",
                                        "value": "B.Sc. Sports Science",
                                        "type": "text",
                                    },
                                    {
                                        "key": "qualifications[0][document]",
                                        "type": "file",
                                        "src": [],
                                    },
                                ],
                            },
                            "url": provider_profile_url,
                        },
                    },
                    {
                        "name": "Update Coach Profile",
                        "request": {
                            "method": "PATCH",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {
                                        "key": "headline",
                                        "value": "Master Elite Fitness Coach",
                                        "type": "text",
                                    },
                                    {
                                        "key": "about",
                                        "value": "Updated bio with 10+ years of personal coaching experience.",
                                        "type": "text",
                                    },
                                    {
                                        "key": "intro_video",
                                        "type": "file",
                                        "src": [],
                                    },
                                    {
                                        "key": "introduction_video_thumbnail",
                                        "type": "file",
                                        "src": [],
                                    },
                                ],
                            },
                            "url": provider_profile_url,
                        },
                    },
                    {
                        "name": "Get Coach Availability",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": provider_availability_url,
                        },
                        "response": make_response_example(
                            "Get Availability Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Coach availability retrieved successfully.",
                                "data": {
                                    "has_availability": True,
                                    "weekly": [
                                        {
                                            "weekday": 0,
                                            "weekday_display": "Monday",
                                            "start_time": "09:00",
                                            "end_time": "17:00",
                                        },
                                        {
                                            "weekday": 2,
                                            "weekday_display": "Wednesday",
                                            "start_time": "10:00",
                                            "end_time": "14:00",
                                        },
                                    ],
                                    "on_call": [
                                        {
                                            "weekday": 0,
                                            "weekday_display": "Monday",
                                            "start_time": "17:00",
                                            "end_time": "21:00",
                                        }
                                    ],
                                    "on_call_enabled": True,
                                    "time_off": [
                                        {
                                            "date": "2026-10-16",
                                            "reason": "Holiday",
                                        }
                                    ],
                                },
                            },
                        ),
                    },
                    {
                        "name": "Update Coach Availability",
                        "request": {
                            "method": "PUT",
                            "header": [
                                {"key": "Authorization", "value": "Bearer {{access_token}}"},
                                {"key": "Content-Type", "value": "application/json"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "weekly": [
                                            {
                                                "weekday": 0,
                                                "weekday_display": "Monday",
                                                "start_time": "09:00",
                                                "end_time": "17:00",
                                            },
                                            {
                                                "weekday": 2,
                                                "weekday_display": "Wednesday",
                                                "start_time": "10:00",
                                                "end_time": "14:00",
                                            },
                                        ],
                                        "on_call": [
                                            {
                                                "weekday": 0,
                                                "weekday_display": "Monday",
                                                "start_time": "17:00",
                                                "end_time": "21:00",
                                            }
                                        ],
                                        "on_call_enabled": True,
                                        "time_off": [
                                            {
                                                "date": "2026-10-16",
                                                "reason": "Holiday",
                                            }
                                        ],
                                    },
                                    indent=2,
                                ),
                            },
                            "url": provider_availability_url,
                        },
                        "response": make_response_example(
                            "Update Availability Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Availability updated successfully.",
                                "data": {
                                    "has_availability": True,
                                    "weekly": [
                                        {
                                            "weekday": 0,
                                            "weekday_display": "Monday",
                                            "start_time": "09:00",
                                            "end_time": "17:00",
                                        },
                                        {
                                            "weekday": 2,
                                            "weekday_display": "Wednesday",
                                            "start_time": "10:00",
                                            "end_time": "14:00",
                                        },
                                    ],
                                    "on_call": [
                                        {
                                            "weekday": 0,
                                            "weekday_display": "Monday",
                                            "start_time": "17:00",
                                            "end_time": "21:00",
                                        }
                                    ],
                                    "on_call_enabled": True,
                                    "time_off": [
                                        {
                                            "date": "2026-10-16",
                                            "reason": "Holiday",
                                        }
                                    ],
                                },
                            },
                        ),
                    },
                    {
                        "name": "Get Coach Reviews",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": provider_reviews_url,
                        },
                        "response": make_response_example(
                            "Get Reviews Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Reviews retrieved successfully.",
                                "data": {
                                    "avg_rating": 5.0,
                                    "total_reviews": 1,
                                    "rating_breakdown": {
                                        "5": 1,
                                        "4": 0,
                                        "3": 0,
                                        "2": 0,
                                        "1": 0,
                                    },
                                    "reviews": [
                                        {
                                            "id": 1,
                                            "user_name": "Jane Buyer",
                                            "user_image": None,
                                            "rating": 5,
                                            "review": "Brilliant session, very practical.",
                                            "created_at": "2026-09-30T05:36:45.966655Z",
                                        }
                                    ],
                                },
                            },
                        ),
                    },
                    {
                        "name": "Get Categories List",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": provider_categories_list_url,
                        },
                        "response": make_response_example(
                            "Get Categories List Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Categories retrieved successfully.",
                                "data": [
                                    {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business",
                                        "is_active": True,
                                        "image": "http://127.0.0.1:8000/media/category_images/Screenshot_2026-06-18_122724.png",
                                    },
                                    {
                                        "id": 2,
                                        "name": "consulting",
                                        "description": "consulting",
                                        "is_active": True,
                                        "image": "http://127.0.0.1:8000/media/category_images/close-up-businesspeople-working-with-documents_1098-1263.avif",
                                    },
                                    {
                                        "id": 3,
                                        "name": "wellness",
                                        "description": "wellness",
                                        "is_active": True,
                                        "image": "http://127.0.0.1:8000/media/category_images/close-up-businesspeople-working-with-documents_1098-1263_TDOjz1K.avif",
                                    },
                                ],
                            },
                        ),
                    },
                ],
            },
            {
                "name": "Coach - Services",
                "item": [
                    {
                        "name": "Create Service",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                },
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                },
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "title": "1:1 Career Session",
                                        "category": 1,
                                        "description": "Plan your next career move.",
                                        "service_type": "one_time",
                                        "session_format": "video",
                                        "session_duration": 60,
                                        "currency": "USD",
                                        "price": "120.00",
                                        "booking_type": "instant",
                                        "who_is_this_service_for": "Engineers",
                                        "preparation_instructions": "Bring your CV",
                                        "cancellation_policy": "standard",
                                        "session_url": "https://meet.google.com/abc-defg-hij",
                                        "status": "published",
                                        "benefits": [
                                            {"outcome": "A clear career plan"},
                                            {"outcome": "CV feedback"},
                                        ],
                                    },
                                    indent=2,
                                ),
                            },
                            "url": provider_services_create_url,
                        },
                        "response": make_response_example(
                            "Create Service Success Example",
                            201,
                            {
                                "success": True,
                                "status": 201,
                                "message": "Service created successfully.",
                                "data": {
                                    "id": 4,
                                    "coach": 4,
                                    "title": "1:1 Career Session",
                                    "description": "Plan your next career move.",
                                    "service_type": "one_time",
                                    "session_format": "video",
                                    "session_duration": 60,
                                    "currency": "USD",
                                    "price": "120.00",
                                    "booking_type": "instant",
                                    "who_is_this_service_for": "Engineers",
                                    "preparation_instructions": "Bring your CV",
                                    "cancellation_policy": "standard",
                                    "session_url": "https://meet.google.com/abc-defg-hij",
                                    "status": "published",
                                    "benefits": [
                                        {"id": 2, "outcome": "A clear career plan"},
                                        {"id": 3, "outcome": "CV feedback"},
                                    ],
                                    "category": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "bookings_count": 0,
                                    "revenue": "0.00",
                                    "created_at": "2026-09-30T05:36:51.620395Z",
                                    "updated_at": "2026-09-30T05:36:51.620395Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "List Services",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "url": {
                                **provider_services_list_url,
                                "query": [
                                    {
                                        "key": "status",
                                        "value": "published",
                                        "description": "Optional status filter (e.g. published). Omit to return all.",
                                    }
                                ],
                            },
                        },
                        "response": make_response_example(
                            "List Services Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Services retrieved successfully.",
                                "data": [
                                    {
                                        "id": 4,
                                        "coach": 4,
                                        "title": "1:1 Career Session",
                                        "description": "Plan your next career move.",
                                        "service_type": "one_time",
                                        "session_format": "video",
                                        "session_duration": 60,
                                        "currency": "USD",
                                        "price": "120.00",
                                        "booking_type": "instant",
                                        "who_is_this_service_for": "Engineers",
                                        "preparation_instructions": "Bring your CV",
                                        "cancellation_policy": "standard",
                                        "session_url": "https://meet.google.com/abc-defg-hij",
                                        "status": "published",
                                        "benefits": [
                                            {"id": 2, "outcome": "A clear career plan"},
                                            {"id": 3, "outcome": "CV feedback"},
                                        ],
                                        "category": {
                                            "id": 1,
                                            "name": "Business",
                                            "description": "Business coaching",
                                        },
                                        "bookings_count": 0,
                                        "revenue": "0.00",
                                        "created_at": "2026-09-30T05:36:51.620395Z",
                                        "updated_at": "2026-09-30T05:36:51.620395Z",
                                    }
                                ],
                            },
                        ),
                    },
                    {
                        "name": "Get Service Detail",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "url": provider_services_detail_url,
                        },
                        "response": make_response_example(
                            "Get Service Detail Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Service retrieved successfully.",
                                "data": {
                                    "id": 1,
                                    "coach": 4,
                                    "title": "Strategy Session",
                                    "description": "A 1:1 strategy session.",
                                    "service_type": "one_time",
                                    "session_format": "video",
                                    "session_duration": 60,
                                    "currency": "USD",
                                    "price": "150.00",
                                    "booking_type": "instant",
                                    "who_is_this_service_for": "Founders and managers",
                                    "preparation_instructions": "Write down your top 3 goals\nBring your latest numbers",
                                    "cancellation_policy": "flexible",
                                    "session_url": "https://meet.google.com/abc-defg-hij",
                                    "status": "published",
                                    "benefits": [
                                        {"id": 1, "outcome": "A clear 90-day plan"}
                                    ],
                                    "category": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "bookings_count": 5,
                                    "revenue": "750.00",
                                    "created_at": "2026-09-30T05:36:45.638870Z",
                                    "updated_at": "2026-09-30T05:36:45.638870Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Update Service",
                        "request": {
                            "method": "PATCH",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                },
                                {
                                    "key": "Content-Type",
                                    "value": "application/json",
                                },
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "title": "Strategy Session",
                                        "price": "160.00",
                                        "booking_type": "instant",
                                        "cancellation_policy": "flexible",
                                        "benefits": [
                                            {"outcome": "A clear 90-day plan"},
                                            {"outcome": "Accountability"},
                                        ],
                                    },
                                    indent=2,
                                ),
                            },
                            "url": provider_services_detail_url,
                        },
                        "response": make_response_example(
                            "Update Service Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Service updated successfully.",
                                "data": {
                                    "id": 1,
                                    "coach": 4,
                                    "title": "Strategy Session",
                                    "description": "A 1:1 strategy session.",
                                    "service_type": "one_time",
                                    "session_format": "video",
                                    "session_duration": 60,
                                    "currency": "USD",
                                    "price": "160.00",
                                    "booking_type": "instant",
                                    "who_is_this_service_for": "Founders and managers",
                                    "preparation_instructions": "Write down your top 3 goals\nBring your latest numbers",
                                    "cancellation_policy": "flexible",
                                    "session_url": "https://meet.google.com/abc-defg-hij",
                                    "status": "published",
                                    "benefits": [
                                        {"id": 4, "outcome": "A clear 90-day plan"},
                                        {"id": 5, "outcome": "Accountability"},
                                    ],
                                    "category": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "bookings_count": 5,
                                    "revenue": "750.00",
                                    "created_at": "2026-09-30T05:36:45.638870Z",
                                    "updated_at": "2026-09-30T05:36:51.644276Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Delete Service",
                        "request": {
                            "method": "DELETE",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "url": provider_services_delete_url,
                        },
                        "response": make_response_example(
                            "Delete Service Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Service deleted successfully.",
                                "data": {"id": 3},
                            },
                        ),
                    },
                ],
            },
            {
                "name": "Coach - Blogs",
                "item": [
                    {
                        "name": "Create Blog",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {
                                        "key": "title",
                                        "value": "Five habits of great founders",
                                        "type": "text",
                                    },
                                    {
                                        "key": "category",
                                        "value": "{{category_id}}",
                                        "type": "text",
                                    },
                                    {
                                        "key": "content",
                                        "value": "Long article text...",
                                        "type": "text",
                                    },
                                    {
                                        "key": "status",
                                        "value": "published",
                                        "type": "text",
                                    },
                                    {
                                        "key": "image",
                                        "type": "file",
                                        "src": [],
                                    },
                                ],
                            },
                            "url": provider_blogs_create_url,
                        },
                        "response": make_response_example(
                            "Create Blog Success Example",
                            201,
                            {
                                "success": True,
                                "status": 201,
                                "message": "Blog created successfully.",
                                "data": {
                                    "id": 3,
                                    "coach": 4,
                                    "category": 1,
                                    "category_details": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "title": "Five habits of great founders",
                                    "content": "Long article text...",
                                    "image": "https://4234cwc7-8004.inc1.devtunnels.ms/media/coach/blogs/photo.gif",
                                    "status": "published",
                                    "created_at": "2026-09-30T05:36:51.661056Z",
                                    "updated_at": "2026-09-30T05:36:51.661056Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "List Blogs",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "url": provider_blogs_list_url,
                        },
                        "response": make_response_example(
                            "List Blogs Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Blogs retrieved successfully.",
                                "data": [
                                    {
                                        "id": 3,
                                        "coach": 4,
                                        "category": 1,
                                        "category_details": {
                                            "id": 1,
                                            "name": "Business",
                                            "description": "Business coaching",
                                        },
                                        "title": "Five habits of great founders",
                                        "content": "Long article text...",
                                        "image": "https://4234cwc7-8004.inc1.devtunnels.ms/media/coach/blogs/photo.gif",
                                        "status": "published",
                                        "created_at": "2026-09-30T05:36:51.661056Z",
                                        "updated_at": "2026-09-30T05:36:51.661056Z",
                                    },
                                    {
                                        "id": 1,
                                        "coach": 4,
                                        "category": 1,
                                        "category_details": {
                                            "id": 1,
                                            "name": "Business",
                                            "description": "Business coaching",
                                        },
                                        "title": "How to Build Confidence",
                                        "content": "Confidence is key. Confidence is key. Confidence is key...",
                                        "image": None,
                                        "status": "published",
                                        "created_at": "2026-09-30T05:36:45.669031Z",
                                        "updated_at": "2026-09-30T05:36:45.669031Z",
                                    },
                                ],
                            },
                        ),
                    },
                    {
                        "name": "Get Blog Detail",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "url": provider_blogs_detail_url,
                        },
                        "response": make_response_example(
                            "Get Blog Detail Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Blog retrieved successfully.",
                                "data": {
                                    "id": 1,
                                    "coach": 4,
                                    "category": 1,
                                    "category_details": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "title": "How to Build Confidence",
                                    "content": "Confidence is key. Confidence is key...",
                                    "image": None,
                                    "status": "published",
                                    "created_at": "2026-09-30T05:36:45.669031Z",
                                    "updated_at": "2026-09-30T05:36:45.669031Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Update Blog",
                        "request": {
                            "method": "PATCH",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {
                                        "key": "title",
                                        "value": "Five habits of great founders (Updated)",
                                        "type": "text",
                                    },
                                    {
                                        "key": "category",
                                        "value": "{{category_id}}",
                                        "type": "text",
                                    },
                                    {
                                        "key": "content",
                                        "value": "Updated article text...",
                                        "type": "text",
                                    },
                                    {
                                        "key": "status",
                                        "value": "published",
                                        "type": "text",
                                    },
                                    {
                                        "key": "image",
                                        "type": "file",
                                        "src": [],
                                    },
                                ],
                            },
                            "url": provider_blogs_detail_url,
                        },
                        "response": make_response_example(
                            "Update Blog Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Blog updated successfully.",
                                "data": {
                                    "id": 3,
                                    "coach": 4,
                                    "category": 1,
                                    "category_details": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "title": "Five habits of great founders (Updated)",
                                    "content": "Updated article text...",
                                    "image": "https://4234cwc7-8004.inc1.devtunnels.ms/media/coach/blogs/photo.gif",
                                    "status": "published",
                                    "created_at": "2026-09-30T05:36:51.661056Z",
                                    "updated_at": "2026-09-30T05:37:10.123456Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Delete Blog",
                        "request": {
                            "method": "DELETE",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "url": provider_blogs_delete_url,
                        },
                        "response": make_response_example(
                            "Delete Blog Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Blog deleted successfully.",
                                "data": {"id": 2},
                            },
                        ),
                    },
                ],
            },
            {
                "name": "Coach - Products",
                "item": [
                    {
                        "name": "Create Product",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {
                                        "key": "title",
                                        "value": "Interview Workbook",
                                        "type": "text",
                                    },
                                    {
                                        "key": "description",
                                        "value": "Practice questions",
                                        "type": "text",
                                    },
                                    {
                                        "key": "category",
                                        "value": "{{category_id}}",
                                        "type": "text",
                                    },
                                    {
                                        "key": "price",
                                        "value": "19.00",
                                        "type": "text",
                                    },
                                    {
                                        "key": "status",
                                        "value": "published",
                                        "type": "text",
                                    },
                                    {
                                        "key": "Thumbnail",
                                        "type": "file",
                                        "src": [],
                                    },
                                    {
                                        "key": "book_file",
                                        "type": "file",
                                        "src": [],
                                    },
                                ],
                            },
                            "url": provider_products_create_url,
                        },
                        "response": make_response_example(
                            "Create Product Success Example",
                            201,
                            {
                                "success": True,
                                "status": 201,
                                "message": "Product created successfully.",
                                "data": {
                                    "id": 3,
                                    "coach": 4,
                                    "category": 1,
                                    "category_details": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "title": "Interview Workbook",
                                    "description": "Practice questions",
                                    "Thumbnail": "https://4234cwc7-8004.inc1.devtunnels.ms/media/coach/products/photo.gif",
                                    "download_url": "https://4234cwc7-8004.inc1.devtunnels.ms/api/v1/user/digital-product-download/3/",
                                    "preview_file": None,
                                    "page_count": None,
                                    "preview_page_count": None,
                                    "file_type": "PDF",
                                    "price": "19.00",
                                    "status": "published",
                                    "sales_count": 0,
                                    "revenue": "0.00",
                                    "created_at": "2026-09-30T05:36:51.694109Z",
                                    "updated_at": "2026-09-30T05:36:51.694109Z",
                                },
                            },
                        ),
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData && jsonData.data && jsonData.data.id) {",
                                        '    pm.collectionVariables.set("product_id", jsonData.data.id);',
                                        "}",
                                    ],
                                    "type": "text/javascript",
                                },
                            }
                        ],
                    },
                    {
                        "name": "List Products",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "url": provider_products_list_url,
                        },
                        "response": make_response_example(
                            "List Products Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Products retrieved successfully.",
                                "data": [
                                    {
                                        "id": 3,
                                        "coach": 4,
                                        "category": 1,
                                        "category_details": {
                                            "id": 1,
                                            "name": "Business",
                                            "description": "Business coaching",
                                        },
                                        "title": "Interview Workbook",
                                        "description": "Practice questions",
                                        "Thumbnail": "https://4234cwc7-8004.inc1.devtunnels.ms/media/coach/products/photo.gif",
                                        "download_url": "https://4234cwc7-8004.inc1.devtunnels.ms/api/v1/user/digital-product-download/3/",
                                        "preview_file": None,
                                        "page_count": None,
                                        "preview_page_count": None,
                                        "file_type": "PDF",
                                        "price": "19.00",
                                        "status": "published",
                                        "sales_count": 0,
                                        "revenue": "0.00",
                                        "created_at": "2026-09-30T05:36:51.694109Z",
                                        "updated_at": "2026-09-30T05:36:51.694109Z",
                                    },
                                    {
                                        "id": 2,
                                        "coach": 4,
                                        "category": 1,
                                        "category_details": {
                                            "id": 1,
                                            "name": "Business",
                                            "description": "Business coaching",
                                        },
                                        "title": "Old Guide",
                                        "description": "x",
                                        "Thumbnail": None,
                                        "download_url": None,
                                        "preview_file": None,
                                        "page_count": None,
                                        "preview_page_count": None,
                                        "file_type": None,
                                        "price": "9.00",
                                        "status": "draft",
                                        "sales_count": 0,
                                        "revenue": "0.00",
                                        "created_at": "2026-09-30T05:36:45.664895Z",
                                        "updated_at": "2026-09-30T05:36:45.664895Z",
                                    },
                                    {
                                        "id": 1,
                                        "coach": 4,
                                        "category": 1,
                                        "category_details": {
                                            "id": 1,
                                            "name": "Business",
                                            "description": "Business coaching",
                                        },
                                        "title": "Founder Playbook",
                                        "description": "A practical guide.",
                                        "Thumbnail": "https://4234cwc7-8004.inc1.devtunnels.ms/media/coach/products/cover.gif",
                                        "download_url": "https://4234cwc7-8004.inc1.devtunnels.ms/api/v1/user/digital-product-download/1/",
                                        "preview_file": None,
                                        "page_count": None,
                                        "preview_page_count": None,
                                        "file_type": "PDF",
                                        "price": "29.00",
                                        "status": "published",
                                        "sales_count": 1,
                                        "revenue": "29.00",
                                        "created_at": "2026-09-30T05:36:45.652379Z",
                                        "updated_at": "2026-09-30T05:36:45.660086Z",
                                    },
                                ],
                            },
                        ),
                    },
                    {
                        "name": "Get Product Detail",
                        "request": {
                            "method": "GET",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "url": provider_products_detail_url,
                        },
                        "response": make_response_example(
                            "Get Product Detail Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Product retrieved successfully.",
                                "data": {
                                    "id": 1,
                                    "coach": 4,
                                    "category": 1,
                                    "category_details": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "title": "Founder Playbook",
                                    "description": "A practical guide.",
                                    "Thumbnail": "https://4234cwc7-8004.inc1.devtunnels.ms/media/coach/products/cover.gif",
                                    "download_url": "https://4234cwc7-8004.inc1.devtunnels.ms/api/v1/user/digital-product-download/1/",
                                    "preview_file": None,
                                    "page_count": None,
                                    "preview_page_count": None,
                                    "file_type": "PDF",
                                    "price": "29.00",
                                    "status": "published",
                                    "sales_count": 1,
                                    "revenue": "29.00",
                                    "created_at": "2026-09-30T05:36:45.652379Z",
                                    "updated_at": "2026-09-30T05:36:45.660086Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Update Product",
                        "request": {
                            "method": "PATCH",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {
                                        "key": "price",
                                        "value": "25.00",
                                        "type": "text",
                                    },
                                ],
                            },
                            "url": provider_products_update_url,
                        },
                        "response": make_response_example(
                            "Update Product Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Product updated successfully.",
                                "data": {
                                    "id": 1,
                                    "coach": 4,
                                    "category": 1,
                                    "category_details": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "title": "Founder Playbook",
                                    "description": "A practical guide.",
                                    "Thumbnail": "https://4234cwc7-8004.inc1.devtunnels.ms/media/coach/products/cover.gif",
                                    "download_url": "https://4234cwc7-8004.inc1.devtunnels.ms/api/v1/user/digital-product-download/1/",
                                    "preview_file": None,
                                    "page_count": None,
                                    "preview_page_count": None,
                                    "file_type": "PDF",
                                    "price": "25.00",
                                    "status": "published",
                                    "sales_count": 1,
                                    "revenue": "29.00",
                                    "created_at": "2026-09-30T05:36:45.652379Z",
                                    "updated_at": "2026-09-30T05:36:51.767386Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Delete Product",
                        "request": {
                            "method": "DELETE",
                            "header": [
                                {
                                    "key": "Authorization",
                                    "value": "Bearer {{access_token}}",
                                }
                            ],
                            "url": provider_products_delete_url,
                        },
                        "response": make_response_example(
                            "Delete Product Success Example",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Product deleted successfully.",
                                "data": {"id": 2},
                            },
                        ),
                    },
                ],
            },
            {
                "name": "Client - Browse",
                "item": [
                    {
                        "name": "User Category List",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_category_list_url,
                        },
                    },
                    {
                        "name": "Coach Profile List",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_coach_profile_list_url,
                        },
                    },
                    {
                        "name": "Recommended Coach Profile List",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_recommended_coaches_url,
                        },
                    },
                    {
                        "name": "Coach Profile Detail",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_coach_detail_url,
                        },
                    },
                    {
                        "name": "Coach Availability (Date)",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_coach_avail_date_url,
                        },
                    },
                    {
                        "name": "Coach Availability (Month)",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_coach_avail_month_url,
                        },
                    },
                    {
                        "name": "Coach Reviews",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_coach_reviews_url,
                        },
                    },
                    {
                        "name": "User Service List",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_service_list_url,
                        },
                    },
                    {
                        "name": "User Service Detail",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_service_detail_url,
                        },
                    },
                    {
                        "name": "Digital Product List",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_digital_product_list_url,
                        },
                        "response": make_response_example(
                            "Digital Product List Success",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Digital products retrieved successfully.",
                                "data": [
                                    {
                                        "id": 3,
                                        "coach": {
                                            "id": 4,
                                            "coach_profile_id": 1,
                                            "full_name": "Sarah Chen",
                                            "email": "coach@coach.test",
                                            "phone_number": "",
                                            "address": "New York, USA",
                                            "rating": 5.0,
                                            "review_count": 1,
                                            "headline": "Executive & Startup Coach",
                                            "profile_photo": "http://127.0.0.1:8000/media/coach/profile/sarah.gif",
                                            "about": "I help founders scale.",
                                        },
                                        "category": 1,
                                        "category_details": {
                                            "id": 1,
                                            "name": "Business",
                                            "description": "Business coaching",
                                        },
                                        "title": "Interview Workbook",
                                        "description": "Practice questions",
                                        "Thumbnail": "http://127.0.0.1:8000/media/coach/products/photo.gif",
                                        "book_file": None,
                                        "preview_file": None,
                                        "price": "19.99",
                                        "is_published": True,
                                        "is_purchased": False,
                                        "created_at": "2026-03-31T05:32:00.672462Z",
                                        "updated_at": "2026-03-31T05:32:00.672488Z",
                                    }
                                ],
                            },
                        ),
                    },
                    {
                        "name": "Digital Product Detail",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_digital_product_detail_url,
                        },
                        "response": make_response_example(
                            "Digital Product Detail Success",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Digital product details retrieved successfully.",
                                "data": {
                                    "id": 3,
                                    "coach": {
                                        "id": 4,
                                        "coach_profile_id": 1,
                                        "full_name": "Sarah Chen",
                                        "email": "coach@coach.test",
                                        "phone_number": "",
                                        "address": "New York, USA",
                                        "rating": 5.0,
                                        "review_count": 1,
                                        "headline": "Executive & Startup Coach",
                                        "profile_photo": "http://127.0.0.1:8000/media/coach/profile/sarah.gif",
                                        "about": "I help founders scale.",
                                    },
                                    "category": 1,
                                    "category_details": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "title": "Interview Workbook",
                                    "description": "Practice questions",
                                    "Thumbnail": "http://127.0.0.1:8000/media/coach/products/photo.gif",
                                    "book_file": None,
                                    "preview_file": None,
                                    "price": "19.99",
                                    "is_published": True,
                                    "is_purchased": False,
                                    "created_at": "2026-03-31T05:32:00.672462Z",
                                    "updated_at": "2026-03-31T05:32:00.672488Z",
                                    "other_products": [],
                                },
                            },
                        ),
                    },
                    {
                        "name": "Digital Product Download",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_digital_product_download_url,
                        },
                    },
                    {
                        "name": "User Blog List",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_blog_list_url,
                        },
                        "response": make_response_example(
                            "User Blog List Success",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Blogs retrieved successfully.",
                                "data": [
                                    {
                                        "id": 3,
                                        "coach": {
                                            "id": 4,
                                            "coach_profile_id": 1,
                                            "full_name": "Sarah Chen",
                                            "email": "coach@coach.test",
                                            "phone_number": "",
                                            "address": "New York, USA",
                                            "rating": 5.0,
                                            "review_count": 1,
                                            "headline": "Executive & Startup Coach",
                                            "profile_photo": "http://127.0.0.1:8000/media/coach/profile/sarah.gif",
                                            "about": "I help founders scale.",
                                        },
                                        "category": 1,
                                        "category_details": {
                                            "id": 1,
                                            "name": "Business",
                                            "description": "Business coaching",
                                        },
                                        "title": "Five habits of great founders",
                                        "content": "Long article text...",
                                        "image": "http://127.0.0.1:8000/media/coach/blogs/photo.gif",
                                        "status": "published",
                                        "read_time_minutes": 1,
                                        "created_at": "2026-09-30T05:36:51.661056Z",
                                        "updated_at": "2026-09-30T05:36:51.661056Z",
                                    }
                                ],
                            },
                        ),
                    },
                    {
                        "name": "User Blog Detail",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_blog_detail_url,
                        },
                        "response": make_response_example(
                            "User Blog Detail Success",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "Blog details retrieved successfully.",
                                "data": {
                                    "id": 1,
                                    "coach": {
                                        "id": 4,
                                        "coach_profile_id": 1,
                                        "full_name": "Sarah Chen",
                                        "email": "coach@coach.test",
                                        "phone_number": "",
                                        "address": "New York, USA",
                                        "rating": 5.0,
                                        "review_count": 1,
                                        "headline": "Executive & Startup Coach",
                                        "profile_photo": "http://127.0.0.1:8000/media/coach/profile/sarah.gif",
                                        "about": "I help founders scale.",
                                    },
                                    "category": 1,
                                    "category_details": {
                                        "id": 1,
                                        "name": "Business",
                                        "description": "Business coaching",
                                    },
                                    "title": "How to Build Real Confidence",
                                    "content": "Confidence is key...",
                                    "image": None,
                                    "status": "published",
                                    "read_time_minutes": 2,
                                    "created_at": "2026-09-30T05:36:45.669031Z",
                                    "updated_at": "2026-09-30T05:36:51.674795Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Get App Rating Stats",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_app_rating_url,
                        },
                        "response": make_response_example(
                            "Get App Rating Stats Success",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "App rating stats retrieved successfully.",
                                "data": {
                                    "average_rating": 0,
                                    "total_ratings": 0,
                                    "has_rated": False,
                                    "user_rating": None,
                                },
                            },
                        ),
                    },
                    {
                        "name": "Submit App Rating",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Authorization", "value": "Bearer {{access_token}}"},
                                {"key": "Content-Type", "value": "application/json"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "rating": 5,
                                        "review": "Great app!",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": client_app_rating_url,
                        },
                        "response": make_response_example(
                            "Submit App Rating Success",
                            201,
                            {
                                "success": True,
                                "status": 201,
                                "message": "App rating submitted successfully.",
                                "data": {
                                    "id": 1,
                                    "user": 2,
                                    "user_name": "Thomas Client Jr.",
                                    "rating": 5,
                                    "review": "Great app!",
                                    "created_at": "2026-09-30T05:36:52.330371Z",
                                    "updated_at": "2026-09-30T05:36:52.330371Z",
                                },
                            },
                        ),
                    },
                    {
                        "name": "Get App Ratings List",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}],
                            "url": client_app_ratings_list_url,
                        },
                        "response": make_response_example(
                            "Get App Ratings List Success",
                            200,
                            {
                                "success": True,
                                "status": 200,
                                "message": "App ratings retrieved successfully.",
                                "data": [
                                    {
                                        "id": 1,
                                        "user": 2,
                                        "user_name": "Thomas Client Jr.",
                                        "image": "https://4234cwc7-8004.inc1.devtunnels.ms/media/profile_images/photo.gif",
                                        "rating": 5,
                                        "review": "Great app!",
                                        "created_at": "2026-09-30T05:36:52.330371Z",
                                        "updated_at": "2026-09-30T05:36:52.330371Z",
                                    }
                                ],
                            },
                        ),
                    },
                ],
            },
            {
                "name": "Client - Booking & Payments",
                "item": [
                    {
                        "name": "Book a Coach Service",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{access_token}}"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "service_id": 1,
                                        "booking_date": "2026-11-05",
                                        "booking_time": "03:00 PM",
                                        "referral_code": "",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": client_book_service_url,
                        },
                        "response": make_response_example(
                            "Book Coach Service Success",
                            201,
                            {
                                "success": True,
                                "code": 201,
                                "status": 201,
                                "message": "Service order created successfully.",
                                "data": {
                                    "id": 1,
                                    "user": {
                                        "id": 2,
                                        "full_name": "Thomas Client Jr.",
                                        "email": "client@example.com",
                                        "phone_number": "+1234567890",
                                    },
                                    "coach": {
                                        "id": 1,
                                        "full_name": "Sarah Chen",
                                        "email": "coach@example.com",
                                        "phone_number": "",
                                        "profile_photo": None,
                                        "about": "I help founders scale.",
                                    },
                                    "service": {
                                        "id": 1,
                                        "title": "Strategy Session",
                                        "description": "1-on-1 strategy coaching call.",
                                        "service_type": "one_time",
                                        "session_format": "video",
                                        "session_duration": 60,
                                        "price": "160.00",
                                        "currency": "USD",
                                        "booking_type": "instant",
                                        "session_url": None,
                                        "category": {
                                            "id": 1,
                                            "name": "Business",
                                            "description": "",
                                        },
                                    },
                                    "product": None,
                                    "order_type": "service",
                                    "booking_date": "2026-11-05",
                                    "booking_time": "03:00 PM",
                                    "amount": "160.00",
                                    "client_fee": "4.80",
                                    "client_fee_percent": "3.00",
                                    "total_amount": "164.80",
                                    "coach_fee": "8.00",
                                    "coach_fee_percent": "5.00",
                                    "coach_earning": "152.00",
                                    "currency": "USD",
                                    "status": "pending",
                                    "payment_status": "pending",
                                    "payment_method": None,
                                    "transaction_id": None,
                                    "is_on_call": False,
                                    "payment_due_at": "2026-11-05T03:15:00Z",
                                    "created_at": "2026-10-29T10:00:00Z",
                                    "updated_at": "2026-10-29T10:00:00Z",
                                },
                            },
                        ),
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData && jsonData.data && jsonData.data.id) {",
                                        '    pm.collectionVariables.set("booking_id", jsonData.data.id.toString());',
                                        "}",
                                    ],
                                    "type": "text/javascript",
                                },
                            }
                        ],
                    },
                    {
                        "name": "Create Stripe Checkout Session",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{access_token}}"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "booking_id": 1,
                                        "success_url": "https://yourapp.com/payment/success?session_id={CHECKOUT_SESSION_ID}",
                                        "cancel_url": "https://yourapp.com/payment/cancel",
                                        "credit_used": "0.00",
                                    },
                                    indent=2,
                                ),
                            },
                            "url": client_stripe_checkout_url,
                        },
                        "response": make_response_example(
                            "Create Checkout Session Success",
                            200,
                            {
                                "success": True,
                                "code": 200,
                                "status": 200,
                                "message": "Checkout session created successfully.",
                                "data": {
                                    "session_id": "cs_test_a1b2c3d4e5f6",
                                    "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_a1b2c3d4e5f6",
                                    "is_free": False,
                                    "booking_id": 1,
                                    "price": "160.00",
                                    "client_fee": "4.80",
                                    "client_fee_percent": "3.00",
                                    "total": "164.80",
                                    "credit_used": "0.00",
                                    "payable": "164.80",
                                    "currency": "USD",
                                },
                            },
                        ),
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData && jsonData.data) {",
                                        "    if (jsonData.data.session_id) {",
                                        '        pm.collectionVariables.set("checkout_session_id", jsonData.data.session_id);',
                                        "    }",
                                        "    if (jsonData.data.checkout_url) {",
                                        '        pm.collectionVariables.set("checkout_url", jsonData.data.checkout_url);',
                                        "    }",
                                        "}",
                                    ],
                                    "type": "text/javascript",
                                },
                            }
                        ],
                    },
                    {
                        "name": "Stripe Webhook",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "stripe-signature", "value": "{{stripe_signature}}"},
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "id": "evt_test_123456789",
                                        "type": "checkout.session.completed",
                                        "data": {
                                            "object": {
                                                "id": "cs_test_a1b2c3d4e5f6",
                                                "payment_intent": "pi_test_123456789",
                                                "payment_status": "paid",
                                                "metadata": {
                                                    "booking_id": "1",
                                                },
                                            }
                                        },
                                    },
                                    indent=2,
                                ),
                            },
                            "url": client_stripe_webhook_url,
                        },
                        "response": make_response_example(
                            "Stripe Webhook Handled Success",
                            200,
                            {
                                "received": True,
                                "event": "checkout.session.completed",
                                "booking_id": 1,
                                "status": "confirmed",
                                "payment_status": "paid",
                                "transaction_id": "pi_test_123456789",
                            },
                        ),
                    },
                ],
            },
        ],
    }


    return collection


def generate_postman_json():
    collection_data = build_postman_collection()
    out_file = Path("Personal_Project.postman_collection.json")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(collection_data, f, indent=2)

    print(f"Successfully generated Postman Collection: {out_file.resolve()}")


if __name__ == "__main__":
    generate_postman_json()
