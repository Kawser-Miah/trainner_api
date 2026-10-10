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
